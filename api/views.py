import requests
import json
import csv
import zipfile
import tempfile
import uuid
import boto3
import sys
import re
import time
import xml.etree.ElementTree as ET
from io import BytesIO
from botocore.exceptions import ClientError
from collections import defaultdict

from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Case, When

from rest_framework import viewsets, generics, mixins, permissions
from rest_framework import status as httpstatus
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .serializers import *
from .models import *
from .permissions import AdminPermissionOrReadOnly


SERVER_URL = "https://ip-10-0-16-250.ec2.internal/api/workflows/v1"
WORKFLOW_URL = "https://raw.githubusercontent.com/broadinstitute/adapt-pipes/main/adapt_web.wdl"
NCBI_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_TAX_URL = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip"
NCBI_NEIGHBORS_URL = "https://www.ncbi.nlm.nih.gov/genomes/GenomesGroup.cgi?taxid=10239&cmd=download2"

QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/default-Adapt-Cromwell-54-Core"
IMAGE = "quay.io/broadinstitute/adaptcloud"
STORAGE_BUCKET = "adaptwebstorage"
CROMWELL_BUCKET = "adapt-cromwell-54"

with open('./api/aws_config.txt') as f:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = f.read().splitlines()

CONTACT = "adapt@broadinstitute.org"
SUCCESSFUL_STATES = ["Succeeded"]
FAILED_STATES = ["Failed", "Aborted"]
OBJECTIVES = ["maximize-activity", "minimize-guides"]
MAX_ALGS = ["random-greedy", "greedy"]
FINAL_STATES = SUCCESSFUL_STATES + FAILED_STATES
# Store the unambiguous bases that make up each
# ambiguous base in the IUPAC notation
FASTA_CODES = {'A': set(('A')),
               'T': set(('T')),
               'C': set(('C')),
               'G': set(('G')),
               'K': set(('G', 'T')),
               'M': set(('A', 'C')),
               'R': set(('A', 'G')),
               'Y': set(('C', 'T')),
               'S': set(('C', 'G')),
               'W': set(('A', 'T')),
               'B': set(('C', 'G', 'T')),
               'V': set(('A', 'C', 'G')),
               'H': set(('A', 'C', 'T')),
               'D': set(('A', 'G', 'T')),
               'N': set(('A', 'T', 'C', 'G'))}


BOOL_OPT_INPUT_VARS = [
    'write_aln',
]
STR_OPT_INPUT_VARS = [
    'segment',
    'maximization_algorithm',
    'require_flanking3',
    'require_flanking5'
]
POS_INT_OPT_INPUT_VARS = [
    'gl',
    'pl',
    'bestntargets',
    'max_primers_at_site',
    'max_target_length',
    'hard_guide_constraint',
    'rand_sample',
    'memory',
]
NONNEG_INT_OPT_INPUT_VARS = [
    'taxid',
    'pm',
    'idm',
    'gm',
    'soft_guide_constraint',
    'rand_seed',
]
INT_OPT_INPUT_VARS = POS_INT_OPT_INPUT_VARS + NONNEG_INT_OPT_INPUT_VARS
FRAC_OPT_INPUT_VARS = [
    'pp',
    'primer_gc_lo',
    'primer_gc_hi',
    'idfrac',
    'gp',
]
NONNEG_FLOAT_OPT_INPUT_VARS = [
    'objfnweights_a',
    'objfnweights_b',
    'cluster_threshold',
    'penalty_strength',
]
FLOAT_OPT_INPUT_VARS = FRAC_OPT_INPUT_VARS + NONNEG_FLOAT_OPT_INPUT_VARS
UPLOADED_FILES_INPUT_VARS = ['fasta[]', 'specificity_fasta[]']
FILES_INPUT_VARS = UPLOADED_FILES_INPUT_VARS + ['specificity_taxa']
GL_DEFAULT = 28
PL_DEFAULT = 30
SOFT_GUIDE_DEFAULT = 1
P_GC_LO_DEFAULT = 0.35
P_GC_HI_DEFAULT = 0.65

LINEAGE_RANKS = ['family', 'genus', 'species', 'subspecies', 'segment']


def _valid_genome(genome):
    for char in genome:
        if char not in FASTA_CODES:
            return False
    return True


def _format(val):
    formatted_val = val.replace(' ', '_')
    formatted_val = formatted_val.replace('(', '_')
    formatted_val = formatted_val.replace(')', '_')
    return formatted_val


def _metadata(cromwell_id):
    if cromwell_id.startswith('example'):
        return {'outputs': {"adapt_web.guides": ['s3://adaptwebstorage/example_files/example_results.tsv'],
                            "adapt_web.alns": ['s3://adaptwebstorage/example_files/example_alignment.fasta'],
                            "adapt_web.anns": ['s3://adaptwebstorage/example_files/example_annotation.tsv']}}
    try:
        cromwell_response = requests.get("%s/%s/metadata" %(SERVER_URL, cromwell_id), verify=False)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
        requests.exceptions.Timeout):
        content = {'Connection Error': "Unable to connect to our servers. "
            "Try again in a few minutes. If it still doesn't work, "
            "contact %s." %CONTACT}
        return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)
    return cromwell_response.json()


def _files(s3_file_paths):
    output_files = []
    try:
        # in outputs, there should just be 1 output variable (<wdl name>.guides),
        # which contains a dictionary of key file number, value file
        S3 = boto3.client("s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        for s3_file_path in s3_file_paths:
            if s3_file_path.startswith("s3://"):
                folders = s3_file_path.split("/")
                key = "/".join(folders[3:])
                bucket = folders[2]
            else:
                content = {'Server Error': "Output file path incorrectly formatted. "
                "Please contact %s with your run ID." %CONTACT}
                return Response(content, status=httpstatus.HTTP_502_BAD_GATEWAY)
            output_files.append(S3.get_object(Bucket = bucket, Key = key)["Body"])
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            # This would only be possible if Cromwell didn't upload to S3 properly
            # or if S3 lost data
            content = {'Server Error': "Unable to find output files. "
            "Please contact %s with your run ID." %CONTACT}
            return Response(content, status=httpstatus.HTTP_502_BAD_GATEWAY)
        else:
            content = {'Connection Error': "Unable to connect to our file storage. "
                "Try again in a few minutes. If it still doesn't work, "
                "contact %s." %CONTACT}
            return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)
    return output_files


def _result_file_to_dict(output_file):
    content = {}
    lines = output_file.splitlines()
    headers = lines[0].split('\t')
    for i, line in enumerate(lines[1:]):
        raw_content = {headers[k]: val for k,val in enumerate(line.split('\t'))}
        content[i] = {}
        content[i]["rank"] = i
        content[i]["objective_value"] = float(raw_content["objective-value"])
        content[i]["left_primers"] = {
            "frac_bound": float(raw_content["left-primer-frac-bound"]),
            "start_pos": int(raw_content["left-primer-start"])
        }
        content[i]["left_primers"]["primers"] = [
            {
                "target": target
            } \
        for target in raw_content["left-primer-target-sequences"].split(" ")]
        content[i]["right_primers"] = {
            "frac_bound": float(raw_content["right-primer-frac-bound"]),
            "start_pos": int(raw_content["right-primer-start"])
        }
        content[i]["right_primers"]["primers"] = [
            {
                "target": target
            } \
        for target in raw_content["right-primer-target-sequences"].split(" ")]
        content[i]["amplicon_start"] = int(raw_content["target-start"])
        content[i]["amplicon_end"] = int(raw_content["target-end"])
        content[i]["guide_set"] = {
            "frac_bound": float(raw_content["total-frac-bound-by-guides"]),
            "expected_activity": float(raw_content["guide-set-expected-activity"]),
            "median_activity": float(raw_content["guide-set-median-activity"]),
            "fifth_pctile_activity": float(raw_content["guide-set-5th-pctile-activity"])
        }
        start_poses = [
            [
                int(start_pos_i) for start_pos_i in start_pos[1:-1].split(", ")
            ] \
        for start_pos in raw_content["guide-target-sequence-positions"].split(" ")]
        expected_activities = [
            float(expected_activity) \
        for expected_activity in raw_content["guide-expected-activities"].split(" ")]
        targets = raw_content["guide-target-sequences"].split(" ")
        content[i]["guide_set"]["guides"] = [
            {
                "start_pos": start_poses[j],
                "expected_activity": expected_activities[j],
                "target": targets[j]
            } \
        for j in range(len(targets))]
    return content


def _tsv_to_dicts(tsv_file):
    content = []
    lines = tsv_file.splitlines()
    headers = lines[0].split('\t')
    for line in lines[1:]:
        content.append({headers[k]: val for k,val in enumerate(line.split('\t'))})
    return content


def _add_base_to_counts(base, counts):
    if base in counts:
        counts[base] += 1
    elif base in FASTA_CODES:
        for base_option in FASTA_CODES[base]:
            counts[base_option] += 1.0 / len(FASTA_CODES[base])


def _alignment_to_summary(alignment_file):
    summary = []
    seq = []

    # Code if you don't want entropy
    # first = True

    for line in alignment_file.splitlines():
        line = line.rstrip()
        if line.startswith('>'):
            # Code if you don't want entropy
            # if first:
            #     first = False
            #     continue
            # else:
            #     break
            # Code if you want entropy
            seq = "".join(seq)
            if len(summary) == 0:
                summary = [{'A': 0, 'C': 0, 'G': 0, 'T': 0, '-': 0}
                           for _ in seq]
            assert(len(seq) == len(summary))
            for i, base in enumerate(seq):
                _add_base_to_counts(base, summary[i])
            seq = []
        else:
            # Append the sequence
            seq.append(line)

    seq = "".join(seq)
    if len(summary) == 0:
        summary = [{'A': 0, 'C': 0, 'G': 0, 'T': 0, '-': 0}
                   for _ in seq]

    assert(len(seq) == len(summary))
    for i, base in enumerate(seq):
        _add_base_to_counts(base, summary[i])

    return summary


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Produces the various API views for the User Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    The User model is used to log into the Django admin and to
    authenticate admins to update the model list.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TaxonViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Taxon Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = TaxonSerializer

    @action(detail=False, methods=['post'])
    def delete_all(self, request, *args, **kwargs):
        Assay.objects.all().delete()
        AssaySet.objects.all().delete()
        TaxonRank.objects.all().delete()
        Taxon.objects.all().delete()
        Guide.objects.all().delete()
        GuideSet.objects.all().delete()
        Primer.objects.all().delete()
        LeftPrimers.objects.all().delete()
        RightPrimers.objects.all().delete()
        return Response()

    def get_queryset(self):
        rank = self.request.query_params.get('rank')
        if rank:
            qs = Taxon.objects.filter(taxonrank__rank__in=rank.split(',')).distinct()
            return qs
        taxids = self.request.query_params.get('taxid')
        if not taxids:
            return Taxon.objects.all()
        taxids = taxids.split(',')
        taxids_qs = Taxon.objects.filter(taxid=taxids[0])
        if len(taxids) > 1:
            for taxid in taxids[1:]:
                taxids_qs = taxids_qs.union(Taxon.objects.filter(taxid=taxid))
        return taxids_qs


class TaxonRankViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the TaxonRank Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = TaxonRank.objects.all()
    serializer_class = TaxonRankSerializer

    def get_queryset(self):
        designed = self.request.query_params.get('designed')
        if designed:
            qs = TaxonRank.objects.filter(assay_sets__isnull=False).distinct().annotate(
                name=Case(
                    When(rank="segment", then="parent__latin_name"),
                    default="latin_name",
                )).order_by("name", "latin_name")

            return qs

        parents = self.request.query_params.get('parent')
        rank = self.request.query_params.get('rank')
        assays = self.request.query_params.get('assays')
        qs = TaxonRank.objects.all()
        if parents:
            parents = parents.split(',')
            if parents[0] == 'null':
                qs = qs.filter(parent__isnull=True).distinct()
            else:
                qs = qs.filter(parent=parents[0])
            if len(parents) > 1:
                for parent in parents[1:]:
                    if parent == 'null':
                        qs = qs | TaxonRank.objects.filter(parent__isnull=True).distinct()
                    else:
                        qs = qs | TaxonRank.objects.filter(parent=parent).distinct()
        if assays == 'true':
            qs = qs.filter(assay_sets__isnull=False).distinct()
        elif assays == 'false':
            qs = qs.filter(assay_sets__isnull=True).distinct()
        if rank:
            qs = qs.filter(rank=rank)
        return qs

    @action(detail=True)
    def segment_names(self, request, *args, **kwargs):
        taxonrank = self.get_object()
        children = list(taxonrank.children.all())
        segment_names = set()
        while len(children) > 0:
            child = children.pop(0)
            if child.rank == "segment":
                segment_names.add(child.latin_name)
            else:
                children.extend(list(child.children.all()))
        return Response(sorted(segment_names))

    @staticmethod
    def save_by_rank(name, taxrank, taxid=None, parent=None):
        if taxrank not in LINEAGE_RANKS:
            if taxrank == 'no rank' and parent.rank == 'species':
                rank = 'subspecies'
            else:
                return parent
        else:
            rank = taxrank
        taxonrank_data = {'latin_name': name, 'rank': rank}
        if parent:
            taxonrank_data['parent'] = parent.pk
        try:
            taxonrank = get_object_or_404(TaxonRank, **taxonrank_data)
        except Http404:
            serializer = TaxonRankSerializer(data=taxonrank_data)
            serializer.is_valid(raise_exception=True)
            taxonrank = serializer.save()
        if taxid:
            try:
                taxon_data = {'taxid': taxid, 'taxonrank': taxonrank.pk}
                get_object_or_404(Taxon, **taxon_data)
            except Http404:
                serializer = TaxonCreateSerializer(data=taxon_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        return taxonrank

    @staticmethod
    def save_by_taxid(taxid):
        try:
            taxon_obj = get_object_or_404(Taxon, pk=taxid)
            return taxon_obj.taxonrank
        except Http404:
            params = {'db': 'taxonomy', 'id': taxid}
            need_tax_xml = True
            tries = 0
            while need_tax_xml:
                response = requests.get(NCBI_URL, params=params)
                if response.ok:
                    need_tax_xml = False
                elif response.status_code == 429:
                    tries += 1
                    if tries > 5:
                        raise requests.exceptions.HTTPError("NCBI has timed out "
                                                            "too many times.")
                    time.sleep(5)
            tax_xml = response.text
            tax_ET = ET.fromstring(tax_xml)[0]
            tax_name = tax_ET.find('ScientificName').text
            tax_rank = tax_ET.find('Rank').text
            lineage = tax_ET.find('LineageEx')
            parent = None
            for ancestor in lineage.findall('Taxon'):
                ancestor_id = int(ancestor.find('TaxId').text)
                ancestor_name = ancestor.find('ScientificName').text
                ancestor_rank = ancestor.find('Rank').text
                if ancestor_rank in LINEAGE_RANKS:
                    parent = TaxonRankViewSet.save_by_rank(ancestor_name, ancestor_rank, taxid=ancestor_id, parent=parent)
            taxonrank_obj = TaxonRankViewSet.save_by_rank(tax_name, tax_rank, taxid=taxid, parent=parent)
            return taxonrank_obj

    @staticmethod
    def taxon_update():
        # Get taxdump folder and unzip
        ncbi_tax_folder_zip = requests.get(NCBI_TAX_URL)
        viral_taxa = set()
        name_to_taxid = {}
        with zipfile.ZipFile(BytesIO(ncbi_tax_folder_zip.content)) as ncbi_tax_folder:
            # Determine what number the Viruses division is
            # Was 9 as of 2021/02/15, use as default
            viral_division = 9
            try:
                with ncbi_tax_folder.open('division.dmp') as tax_division:
                    for row in tax_division:
                        # Note-no headers, so required to use position in list
                        cells = row.decode("utf-8") .split("\t|\t")
                        if cells[1] == "VRL":
                            viral_division = cells[0]
                            break
            except KeyError: # File does not exist
                pass

            # Determine which tax IDs are viruses
            # Note-files have no headers, so required to use position in list
            with ncbi_tax_folder.open('nodes.dmp') as tax_nodes:
                for row in tax_nodes:
                    cells = row.decode("utf-8").split("\t|\t")
                    if cells[4] == viral_division:
                        viral_taxa.add(cells[0])

            # Determine what the names for the tax IDs are
            with ncbi_tax_folder.open('names.dmp') as tax_names:
                for row in tax_names:
                    cells = row.decode("utf-8").split("\t|\t")
                    taxid = cells[0]
                    name = cells[1]
                    if taxid in viral_taxa:
                        name_to_taxid[name] = int(taxid)
                        # if cells[3].startswith("scientific name"):
                        #     viral_nodes[cells[0]]["latin_name"] = name
                        # else:
                        #     viral_nodes[cells[0]]["description"].append(name + ";")

        ncbi_neighbors_table = requests.get(NCBI_NEIGHBORS_URL)
        prev_name = None
        prev_seg = None
        for row in ncbi_neighbors_table.content.decode("utf-8").split("\r\n"):
            if row.startswith("##"):
                continue
            cells = row.split("\t")
            # hosts = cells[2]
            name = cells[4]
            segment = cells[5]
            if name == prev_name and segment == prev_seg:
                continue
            # if "vertebrate" in hosts or "human" in hosts:
            if name in name_to_taxid:
                taxid = name_to_taxid[name]
                taxonrank_obj = TaxonRankViewSet.save_by_taxid(taxid)
                if segment != "segment  ":
                    # Remove "segment " (8 characters) from segment name
                    segment_name = segment[8:]
                    segment_taxonrank = TaxonRankViewSet.save_by_rank(segment_name, 'segment', parent=taxonrank_obj)
            prev_name = name
            prev_seg = segment

        return Response()

    @action(detail=False, methods=['post'])
    def update_names(self, request, *args, **kwargs):
        # Get taxdump folder and unzip
        ncbi_tax_folder_zip = requests.get(NCBI_TAX_URL)
        taxid_to_alt_names = defaultdict(list)
        taxid_to_latin_names = {}
        with zipfile.ZipFile(BytesIO(ncbi_tax_folder_zip.content)) as ncbi_tax_folder:
            with ncbi_tax_folder.open('names.dmp') as tax_names:
                for row in tax_names:
                    cells = row.decode("utf-8") .split("\t|\t")
                    taxid = int(cells[0])
                    taxon_obj = Taxon.objects.filter(pk=taxid)
                    if taxon_obj.exists():
                        if cells[3].startswith("scientific name"):
                            taxid_to_latin_names[taxid] = name
                        else:
                            taxid_to_alt_names[taxid].append(name)

        for taxid in taxid_to_alt_names:
            taxon_obj = Taxon.objects.get(pk=taxid)
            description = taxid_to_alt_names[taxid].join(";")
            latin_name = taxid_to_latin_names[taxid]
            taxon_serializer = TaxonCreateSerializer(taxon_obj,
                data={'description': description,
                      'latin_name': latin_name},
                partial=True)
            taxon_serializer.save()


class LeftPrimersViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Left Primers Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = LeftPrimers.objects.all()
    serializer_class = LeftPrimersSerializer


class RightPrimersViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Right Primers Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = RightPrimers.objects.all()
    serializer_class = RightPrimersSerializer


class PrimerViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Primer Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = Primer.objects.all()
    serializer_class = PrimerSerializer


class GuideSetViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Guide Set Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = GuideSet.objects.all()
    serializer_class = GuideSetSerializer


class GuideViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Guide Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer


class AssaySetViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Assay Set Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = AssaySet.objects.all()
    serializer_class = AssaySetSerializer

    def get_queryset(self):
        taxonrank = self.request.query_params.get('taxonrank')
        cluster = self.request.query_params.get('cluster')
        created = self.request.query_params.get('created')
        assays = self.request.query_params.get('assays')
        qs = AssaySet.objects.all()
        if taxonrank:
            qs = qs.filter(taxonrank=taxonrank)
        if cluster:
            qs = qs.filter(cluster=cluster)
        if created:
            qs = qs.filter(created=created)
        if assays == 'true':
            qs = qs.filter(assays__isnull=False).distinct()
        elif assays == 'false':
            qs = qs.filter(assays__isnull=True).distinct()
        return qs.order_by('-created')

    @action(detail=False, methods=['post'])
    def clean_up(self, request, *args, **kwargs):
        AssaySet.objects.filter(assays__isnull=True).distinct().delete()

        for _ in range(4):
            taxonrank_pks = [taxrank.pk for taxrank in TaxonRank.objects.all() if (taxrank.num_children == 0 and taxrank.any_assays == False)]
            TaxonRank.objects.filter(pk__in=taxonrank_pks).delete()
        return Response()

    @action(detail=False, methods=['post'], url_path=r'delete_date/(?P<date>[0-9\-]+)')
    def delete_date(self, request, *args, **kwargs):
        AssaySet.objects.filter(created=kwargs["date"]).delete()
        for _ in range(4):
            taxonrank_pks = [taxrank.pk for taxrank in TaxonRank.objects.all() if (taxrank.num_children == 0 and taxrank.any_assays == False)]
            TaxonRank.objects.filter(pk__in=taxonrank_pks).delete()
        return Response()

    @action(detail=True)
    def annotation(self, request, *args, **kwargs):
        """
        Produces a summary of the alignments to display on the site

        Makes a fasta if there is only one file and a ZIP otherwise.
        Function called at the "alignment_summary" API endpoint.
        """
        assay_set = self.get_object()
        content = {}
        if assay_set.s3_ann_path:
            output_file = _files([assay_set.s3_ann_path])[0].read().decode("utf-8")
            content[0] = _tsv_to_dicts(output_file)
            response = Response(content)
            return response
        content = {'Input Error': "There are no annotations for this assay set. "
        "This virus design has likely not been updated recently; you may "
        "want to run this virus again on the 'Run' page of this site."}
        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def alignment_summary(self, request, *args, **kwargs):
        """
        Produces a summary of the alignments to display on the site

        Makes a fasta if there is only one file and a ZIP otherwise.
        Function called at the "alignment_summary" API endpoint.
        """
        assay_set = self.get_object()
        content = {}
        if assay_set.s3_aln_path:
            output_file = _files([assay_set.s3_aln_path])[0].read().decode("utf-8")
            content[0] = _alignment_to_summary(output_file)
            response = Response(content)
            return response
        content = {'Input Error': "There is no alignment for this assay set. "
        "This virus design has likely not been updated recently; you may "
        "want to run this virus again on the 'Run' page of this site."}
        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def alignment(self, request, *args, **kwargs):
        """
        Produces a file of the alignments to download

        Makes a fasta if there is only one taxon and a ZIP otherwise.
        Function called at the "alignment" API endpoint.
        """
        try:
            pks = [int(i) for i in request.query_params.get('pk').split(',')]
        except ValueError:
            content = {'Input Error': "Primary keys must be a comma separated list of integers"}
            return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
        else:
            try:
                assay_sets = [AssaySet.objects.get(pk=pk) for pk in pks]
            except AssaySet.DoesNotExist:
                content = {'Input Error': "At least one of these keys does not point to an assay set."}
            else:
                assay_sets_with_alns = [assay_set for assay_set in assay_sets if assay_set.s3_aln_path]
                if len(assay_sets_with_alns) > 0:
                    files = _files([assay_set.s3_aln_path for assay_set in assay_sets_with_alns])
                    output_files = [file.read().decode("utf-8") for file in files]
                    output_type = "application/zip"
                    # Create the zip file in memory only
                    zipped_output = BytesIO()
                    with zipfile.ZipFile(zipped_output, "a", zipfile.ZIP_DEFLATED) as zipped_output_a:
                        for i, output_file in enumerate(output_files):
                            fastaname = assay_sets_with_alns[i].taxonrank.latin_name
                            if assay_sets_with_alns[i].taxonrank.rank == 'segment':
                                fastaname = "%s_%s" %(assay_sets_with_alns[i].taxonrank.parent.latin_name, fastaname)
                            zipped_output_a.writestr("%s.fasta" %fastaname, output_file)
                    zipped_output.seek(0)
                    filename = "alignments" + "_".join([str(pk) for pk in pks]) + ".zip"
                    response = FileResponse(zipped_output, content_type=output_type)
                    response['Content-Disposition'] = 'attachment; filename=%s' % filename
                    return response
                content = {'Input Error': "There are no alignments for these assay sets. "
                    "This virus design has likely not been updated recently; you may "
                    "want to run this virus again on the 'Run' page of this site."}
        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)


class AssayViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Assay Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [AdminPermissionOrReadOnly]
    serializer_class = AssaySerializer
    queryset = Assay.objects.all()

    @staticmethod
    def update(s3_file_paths, obj, sp, start_time, taxid, tax_seg, alns=None, anns=None):
        """
        Updates the database given the metadata of a single Cromwell job

        """
        if alns:
            if len(alns) != len(s3_file_paths):
                return Response({'Input Error': "If alignments are provided, "
                                 "there must be the same number of alignments "
                                 "as output file paths."},
                                status=httpstatus.HTTP_400_BAD_REQUEST)
        if anns:
            if len(anns) != len(s3_file_paths):
                return Response({'Input Error': "If annotations are provided, "
                                 "there must be the same number of annotations "
                                 "as output file paths."},
                                status=httpstatus.HTTP_400_BAD_REQUEST)
        taxonrank_obj = TaxonRankViewSet.save_by_taxid(int(taxid))
        if tax_seg != 'None':
            taxonrank_obj = TaxonRankViewSet.save_by_rank(tax_seg, 'segment', parent=taxonrank_obj)

        output_files_encoded = _files(s3_file_paths)
        if isinstance(output_files_encoded, Response):
            return output_files_encoded
        output_files = [output_file.read().decode("utf-8") for output_file in output_files_encoded]

        for i, output_file in enumerate(output_files):
            try:
                get_list_or_404(AssaySet,
                    taxonrank=taxonrank_obj.pk,
                    created=start_time,
                    specific=sp,
                    objective=obj,
                    cluster=i)
                continue
            except Http404:
                pass
            lines = output_file.splitlines()
            if len(lines) < 2:
                continue
            aln = alns[i] if alns else ''
            ann = anns[i] if anns else ''
            headers = lines[0].split('\t')
            assay_set_data = {
                'taxonrank': taxonrank_obj.pk,
                'created': start_time,
                'specific': sp,
                'objective': obj,
                'cluster': i,
                's3_aln_path': aln,
                's3_ann_path': ann,
            }
            assay_set = AssaySetSerializer(data=assay_set_data)
            assay_set.is_valid(raise_exception=True)
            assay_set_obj = assay_set.save()
            for j, line in enumerate(lines[1:]):
                raw_content = {headers[k]: val for k,val in enumerate(line.split('\t'))}

                assay_data = {
                    "assay_set": assay_set_obj.pk,
                    "left_primers": {
                        "frac_bound": round(float(raw_content["left-primer-frac-bound"]),16),
                        "start_pos": int(raw_content["left-primer-start"])
                    },
                    "right_primers": {
                        "frac_bound": round(float(raw_content["right-primer-frac-bound"]),16),
                        "start_pos": int(raw_content["right-primer-start"])
                    },
                    "guide_set": {
                        "frac_bound": round(float(raw_content["total-frac-bound-by-guides"]),16),
                        "expected_activity": round(float(raw_content["guide-set-expected-activity"]),16),
                        "median_activity": round(float(raw_content["guide-set-median-activity"]),16),
                        "fifth_pctile_activity": round(float(raw_content["guide-set-5th-pctile-activity"]),16)
                    },
                    'rank': j,
                    'objective_value': round(float(raw_content["objective-value"]),16),
                    'amplicon_start': int(raw_content["target-start"]),
                    'amplicon_end': int(raw_content["target-end"]),
                }
                assay = AssaySerializer(data=assay_data)
                assay.is_valid(raise_exception=True)
                assay_obj = assay.save()

                for target in raw_content["left-primer-target-sequences"].split(" "):
                    primer_data = {
                        "target": target,
                        "left_primer_set": assay_obj.left_primers.pk
                    }
                    primer = PrimerSerializer(data=primer_data)
                    primer.is_valid(raise_exception=True)
                    primer.save()

                for target in raw_content["right-primer-target-sequences"].split(" "):
                    primer_data = {
                        "target": target,
                        "right_primer_set": assay_obj.right_primers.pk
                    }
                    primer = PrimerSerializer(data=primer_data)
                    primer.is_valid(raise_exception=True)
                    primer.save()

                start_poses = [
                    [int(start_pos_i) for start_pos_i in start_pos[1:-1].split(", ")] \
                for start_pos in raw_content["guide-target-sequence-positions"].split(" ")]
                expected_activities = [
                    float(expected_activity) \
                for expected_activity in raw_content["guide-expected-activities"].split(" ")]

                for k, target in enumerate(raw_content["guide-target-sequences"].split(" ")):
                    guide_data = {
                        "start_pos": start_poses[k],
                        "expected_activity": expected_activities[k],
                        "target": target,
                        "guide_set": assay_obj.guide_set.pk
                    }
                    guide = GuideSerializer(data=guide_data)
                    guide.is_valid(raise_exception=True)
                    guide.save()

    @action(detail=False, methods=['post'])
    def database_update(self, request, *args, **kwargs):
        """
        Updates the database given a job ID from Cromwell

        """

        # Call Cromwell server
        metadata_response = _metadata(request.data["id"])
        if isinstance(metadata_response, Response):
            return metadata_response

        objs = metadata_response["inputs"]["objs"]
        sps = metadata_response["inputs"]["sps"]
        tax_to_do = metadata_response["inputs"]["tax_to_do"] if "tax_to_do" in metadata_response["inputs"] else None
        # Get file paths for S3
        if metadata_response["status"] not in SUCCESSFUL_STATES:
            S3 = boto3.client("s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            more_files = True
            continuation_token = None
            s3_file_paths = [[defaultdict(list) for obj in objs] for sp in sps]
            while more_files:
                list_objs_args = {
                    'Bucket': CROMWELL_BUCKET,
                    'Prefix': "cromwell-execution/parallel_adapt/%s/call-Scatter" %request.data["id"],
                }
                if continuation_token:
                    list_objs_args['ContinuationToken'] = continuation_token
                file_response = S3.list_objects_v2(**list_objs_args)
                for file in file_response["Contents"]:
                    if file["Key"].endswith("guides.tsv.0") or file["Key"].endswith("guides.0.tsv"):
                        shards_str = re.findall(r"shard-\d+", file["Key"])
                        shards_int = [int(shard_str[6:]) for shard_str in shards_str]
                        if len(shards_int) != 3:
                            raise ValueError("There are not the correct number of scatter shards "
                                             "(should be 3); check the cromwell ID and the WDL.")
                        shards2 = tax_to_do[shards_int[2]] if tax_to_do else shards_int[2]
                        s3_file_paths[shards_int[0]][shards_int[1]][shards2].append("s3://%s/%s" %(CROMWELL_BUCKET, file["Key"]))
                if file_response["IsTruncated"]:
                    continuation_token = file_response["NextContinuationToken"]
                else:
                    more_files = False
        else:
            s3_file_paths = metadata_response["outputs"]["parallel_adapt.guides"]
        # Parse taxa information and make taxa for those that do not exist in database
        taxa_file_path = metadata_response["inputs"]["taxa_file"]
        start_time = metadata_response["start"][:10]
        taxa_file = _files([taxa_file_path])
        if isinstance(taxa_file, Response):
            return taxa_file
        taxa_lines = taxa_file[0].read().decode("utf-8").splitlines()
        taxa_headers = taxa_lines[0].split('\t')
        taxa = [{taxa_headers[i]: val \
            for i, val in enumerate(taxa_line.split('\t'))} \
            for taxa_line in taxa_lines[1:]]

        for p, sp in enumerate(sps):
            for q, obj in enumerate(objs):
                for r, taxon in enumerate(taxa):
                    tax_seg = taxon['segment']
                    if tax_to_do and r not in tax_to_do:
                        continue
                    if (isinstance(s3_file_paths[p][q], dict) and r not in s3_file_paths[p][q]) or s3_file_paths[p][q][r] == []:
                        continue
                    taxonrank_obj = TaxonRankViewSet.save_by_taxid(int(taxon['taxid']))
                    if tax_seg != 'None':
                        taxonrank_obj = TaxonRankViewSet.save_by_rank(tax_seg, 'segment', parent=taxonrank_obj)

                    output_files_encoded = _files(s3_file_paths[p][q][r])
                    if isinstance(output_files_encoded, Response):
                        return output_files_encoded
                    output_files = [output_file.read().decode("utf-8") for output_file in output_files_encoded]

                    for i, output_file in enumerate(output_files):
                        try:
                            get_list_or_404(AssaySet,
                                taxonrank=taxonrank_obj.pk,
                                created=start_time,
                                specific=sp,
                                objective=obj,
                                cluster=i)
                            continue
                        except Http404:
                            pass
                        lines = output_file.splitlines()
                        if len(lines) < 2:
                            continue
                        headers = lines[0].split('\t')
                        assay_set_data = {
                            'taxonrank': taxonrank_obj.pk,
                            'created': start_time,
                            'specific': sp,
                            'objective': obj,
                            'cluster': i,
                        }
                        assay_set = AssaySetSerializer(data=assay_set_data)
                        assay_set.is_valid(raise_exception=True)
                        assay_set_obj = assay_set.save()
                        for j, line in enumerate(lines[1:]):
                            raw_content = {headers[k]: val for k,val in enumerate(line.split('\t'))}

                            assay_data = {
                                "assay_set": assay_set_obj.pk,
                                "left_primers": {
                                    "frac_bound": round(float(raw_content["left-primer-frac-bound"]),16),
                                    "start_pos": int(raw_content["left-primer-start"])
                                },
                                "right_primers": {
                                    "frac_bound": round(float(raw_content["right-primer-frac-bound"]),16),
                                    "start_pos": int(raw_content["right-primer-start"])
                                },
                                "guide_set": {
                                    "frac_bound": round(float(raw_content["total-frac-bound-by-guides"]),16),
                                    "expected_activity": round(float(raw_content["guide-set-expected-activity"]),16),
                                    "median_activity": round(float(raw_content["guide-set-median-activity"]),16),
                                    "fifth_pctile_activity": round(float(raw_content["guide-set-5th-pctile-activity"]),16)
                                },
                                'rank': j,
                                'objective_value': round(float(raw_content["objective-value"]),16),
                                'amplicon_start': int(raw_content["target-start"]),
                                'amplicon_end': int(raw_content["target-end"]),
                            }
                            assay = AssaySerializer(data=assay_data)
                            assay.is_valid(raise_exception=True)
                            assay_obj = assay.save()

                            for target in raw_content["left-primer-target-sequences"].split(" "):
                                primer_data = {
                                    "target": target,
                                    "left_primer_set": assay_obj.left_primers.pk
                                }
                                primer = PrimerSerializer(data=primer_data)
                                primer.is_valid(raise_exception=True)
                                primer.save()

                            for target in raw_content["right-primer-target-sequences"].split(" "):
                                primer_data = {
                                    "target": target,
                                    "right_primer_set": assay_obj.right_primers.pk
                                }
                                primer = PrimerSerializer(data=primer_data)
                                primer.is_valid(raise_exception=True)
                                primer.save()

                            start_poses = [
                                [int(start_pos_i) for start_pos_i in start_pos[1:-1].split(", ")] \
                            for start_pos in raw_content["guide-target-sequence-positions"].split(" ")]
                            expected_activities = [
                                float(expected_activity) \
                            for expected_activity in raw_content["guide-expected-activities"].split(" ")]

                            for k, target in enumerate(raw_content["guide-target-sequences"].split(" ")):
                                guide_data = {
                                    "start_pos": start_poses[k],
                                    "expected_activity": expected_activities[k],
                                    "target": target,
                                    "guide_set": assay_obj.guide_set.pk
                                }
                                guide = GuideSerializer(data=guide_data)
                                guide.is_valid(raise_exception=True)
                                guide.save()
        return Response({"id": request.data["id"]}, status=httpstatus.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def single_update(self, request, *args, **kwargs):
        """
        Updates the database given s3 file paths, the objective, the specificity,
        the start, and the tax ID

        """
        alns = request.data["s3_aln_paths"] \
            if ("s3_aln_paths" in request.data) else None
        anns = request.data["s3_ann_paths"] \
            if ("s3_ann_paths" in request.data) else None
        AssayViewSet.update(
            request.data["s3_file_paths"],
            request.data["obj"],
            request.data["sp"],
            request.data["start"][:10],
            request.data["taxid"],
            request.data["taxseg"],
            alns=alns,
            anns=anns
        )

        return Response({"id": request.data["taxid"]}, status=httpstatus.HTTP_201_CREATED)

    def get_queryset(self):
        assay_set_str = self.request.query_params.get('assay_set')
        if not assay_set_str:
            return Assay.objects.all()
        assay_sets = assay_set_str.split(',')
        assay_qs = Assay.objects.filter(assay_set=assay_sets[0])
        if len(assay_sets) > 1:
            for assay_set in assay_sets[1:]:
                assay_qs = assay_qs.union(Assay.objects.filter(assay_set=assay_set))
        return assay_qs


class ADAPTRunViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the ADAPT Run Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    Additional actions are created using the @action decorator,
    which creates an API enpoint for the action. This viewset
    overrides create to submit to Cromwell and format data and
    creates custom actions to get the status and results.
    """
    # Allows POST requests to be input in a variety of ways
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = ADAPTRun.objects.all()
    serializer_class = ADAPTRunSerializer


    @staticmethod
    def _check_fasta(file):
        filetypes = [".fasta", ".fa", ".fna", ".ffn", ".faa", ".frn", ".aln", ".txt", ".gz"]
        for filetype in filetypes:
            if file.name.endswith(filetype):
                return True
        return False

    @staticmethod
    def _is_valid(request):
        content = None
        if 'obj' not in request.data:
            content = "The objective value is required."
        elif 'taxid' not in request.data and 'fasta[]' not in request.FILES:
            content = "Either a taxonomic ID or a FASTA file must be included"
        else:
            for input_var, value in request.data.items():
                if input_var == 'obj':
                    if value not in OBJECTIVES:
                        content = "'%s' is an invalid objective; the objective must be one of <ul><li>%s</li></ul>" \
                            %(value, '</li><li>'.join(OBJECTIVES))
                        break
                elif input_var == 'maximization_algorithm':
                    if value not in MAX_ALGS:
                        content = "'%s' is an invalid maximization algorithm; the maximization algorithm must be one of " \
                            "<ul><li>%s</li></ul> Default is '%s'" %(value, '</li><li>'.join(MAX_ALGS), MAX_ALGS[0])
                        break
                elif input_var.startswith('require_flanking'):
                    if not _valid_genome(value):
                        content = "'%s' is an invalid flanking sequence; each character must be one of " \
                            "<ul><li>%s</li></ul>" %(value, '</li><li>'.join(FASTA_CODES.keys()))
                        break
                elif input_var == 'nickname':
                    if len(value) > 50:
                        content = "Nickname '%s' is too long; it must be less than 50 characters." %value
                        break
                elif input_var == 'segment':
                    if value == '':
                        request.data[input_var] = 'None'
                elif input_var in POS_INT_OPT_INPUT_VARS:
                    if (not value.isdigit()) or value == '0':
                        content = "'%s' is invalid for %s; it must be a positive integer" %(value, input_var)
                        break
                    if input_var == 'max_target_length':
                        mod_value = int(value)
                        try:
                            gl = int(request.data['gl']) if 'gl' in request.data else GL_DEFAULT
                            pl = int(request.data['pl']) if 'pl' in request.data else PL_DEFAULT
                            if mod_value < max(gl, pl):
                                content = "'%s' is invalid for %s; it must be at least as large at the primer length and the guide length" %(value, input_var)
                                break
                        except:
                            pass
                    elif input_var == 'hard_guide_constraint':
                        mod_value = int(value)
                        try:
                            soft_guide = int(request.data['soft_guide_constraint']) if 'soft_guide_constraint' in request.data else SOFT_GUIDE_DEFAULT
                            if mod_value < soft_guide:
                                content = "'%s' is invalid for %s; it must be at least as large at the primer length and the guide length" %(value, input_var)
                                break
                        except:
                            pass
                elif input_var in NONNEG_INT_OPT_INPUT_VARS:
                    if not value.isdigit():
                        content = "'%s' is invalid for %s; it must be a nonnegative integer" %(value, input_var)
                        break
                elif input_var in FLOAT_OPT_INPUT_VARS:
                    try:
                        mod_value = float(value)
                    except:
                        content = "'%s' is invalid for %s; it must be a decimal" %(value, input_var)
                        break
                    else:
                        if mod_value < 0:
                            content = "'%s' is invalid for %s; it must be between 0 and 1 (inclusive)" %(value, input_var)
                            break
                        if input_var in FRAC_OPT_INPUT_VARS:
                            if mod_value > 1:
                                content = "'%s' is invalid for %s; it must be between 0 and 1 (inclusive)" %(value, input_var)
                                break
                        if input_var == 'primer_gc_lo':
                            try:
                                primer_gc_hi = float(request.data['primer_gc_hi']) if 'primer_gc_hi' in request.data else P_GC_HI_DEFAULT
                                if mod_value > primer_gc_hi:
                                    content = "'%s' is invalid for the lowest GC primer percent content; it must " \
                                        "be less than the highest GC primer percent content" %value
                                    break
                            except:
                                pass
                        elif input_var == 'primer_gc_hi':
                            try:
                                primer_gc_lo = float(request.data['primer_gc_lo']) if 'primer_gc_lo' in request.data else P_GC_LO_DEFAULT
                                if mod_value < primer_gc_lo:
                                    content = "'%s' is invalid for the highest GC primer percent content; it must " \
                                        "be greater than the lowest GC primer percent content" %value
                                    break
                            except:
                                pass
                elif input_var in BOOL_OPT_INPUT_VARS:
                    if value != 'true' and value != 'false':
                        content = "'%s' is invalid for %s; it must be a boolean of value 'true' or " \
                            "'false'" %(value, input_var)
                        break
                elif input_var not in FILES_INPUT_VARS:
                    content = "%s is not a valid input parameter" % input_var
                    break
        if content:
            return (False, Response({'Input Error': content}, status=httpstatus.HTTP_400_BAD_REQUEST))
        return (True, )

    @staticmethod
    def _get_results(adaptrun, data_format):
        """
        Helper function for download and results
        """
        # Check status of run
        status_response = ADAPTRunViewSet._get_status(adaptrun)
        if status_response.status_code == httpstatus.HTTP_200_OK:
            # Only get results if job succeeded
            if adaptrun.status in SUCCESSFUL_STATES:
                # Call Cromwell server
                metadata_response = _metadata(adaptrun.cromwell_id)
                if isinstance(metadata_response, Response):
                    return metadata_response
                # Download files from S3
                if data_format in ['aln', 'aln_sum']:
                    files = _files(metadata_response["outputs"]["adapt_web.alns"])
                elif data_format == 'ann':
                    if "adapt_web.anns" in metadata_response["outputs"]:
                        files = _files(metadata_response["outputs"]["adapt_web.anns"])
                    else:
                        content = {'Input Error': "There are no annotations for this run. "
                        "This is likely an older run made with a former version; please try rerunning."}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                else:
                    files = _files(metadata_response["outputs"]["adapt_web.guides"])
                if isinstance(files, Response):
                    return files

                if data_format in ['json', 'aln_sum', 'ann']:
                    # try:
                    output_files = [output_file.read().decode("utf-8") for output_file in files]
                    content = {}
                    if data_format == 'json':
                        conversion_function = _result_file_to_dict
                    elif data_format == 'ann':
                        conversion_function = _tsv_to_dicts
                    else:
                        conversion_function = _alignment_to_summary
                    for i, output_file in enumerate(output_files):
                        content[i] = conversion_function(output_file)
                    response = Response(content)
                    # except Exception:
                    #     content = {'Incorrect output formatting': "Job output is incorrectly "
                    #         "formatted, possibly indicating file corruption. Please "
                    #         "contact %s with your run ID to resolve the issue." %CONTACT}
                    #     response = Response(content, status=httpstatus.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    if len(files) == 0:
                        content = {'No output': "Job output does not exist. "
                            "Please contact %s with your run ID to resolve the issue." %CONTACT}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    elif len(files) == 1:
                        # If there is only one file, no need to zip
                        output = files[0].read().decode("utf-8")
                        if data_format == 'aln':
                            output_type = "chemical/seq-na-fasta"
                            output_ext = ".fasta"
                        else:
                            output_type = "text/tsv"
                            output_ext = ".tsv"
                    else:
                        output_files = [output_file.read().decode("utf-8") for output_file in files]
                        output_type = "application/zip"
                        # Create the zip file in memory only
                        zipped_output = BytesIO()
                        with zipfile.ZipFile(zipped_output, "a", zipfile.ZIP_DEFLATED) as zipped_output_a:
                            if data_format == 'aln':
                                for i, output_file in enumerate(output_files):
                                    zipped_output_a.writestr("%s.%i.fasta" %(adaptrun.cromwell_id, i), output_file)
                            else:
                                for i, output_file in enumerate(output_files):
                                    zipped_output_a.writestr("%s.%i.tsv" %(adaptrun.cromwell_id, i), output_file)
                        zipped_output.seek(0)
                        output = zipped_output
                        output_ext = ".zip"
                    if adaptrun.cromwell_id.startswith("example"):
                        filename = adaptrun.cromwell_id+output_ext
                    else:
                        filename = adaptrun.cromwell_id[:8]+output_ext
                    response = FileResponse(output, content_type=output_type)
                    response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response

            elif adaptrun.status in FAILED_STATES:
                # TODO give reasons that the job might fail
                content = {'Failed Job': "Job has failed. "
                    "This could be due to invalid input parameters or "
                    "running out of memory. Please check your input prior "
                    "to your next request, then try increasing memory. "
                    "If you continue to have issues, contact %s" %CONTACT}
                return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

            else:
                content = {'Unfinished Job': "Job is not finished running. "
                    "Please wait until the job is done; this can take a few "
                    "hours on large datasets. You may check your job status "
                    "using 'Get Status'."}
                return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
        else:
            return status_response

    @staticmethod
    def _get_status(adaptrun):
        # Check if the run wasn't finished the last time status was checked
        if adaptrun.status not in FINAL_STATES and not adaptrun.cromwell_id.startswith('example'):
            # Call Cromwell server
            try:
                cromwell_response = requests.get("%s/%s/status" %(SERVER_URL,adaptrun.cromwell_id), verify=False)
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
                content = {'Connection Error': "Unable to connect to our servers. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)
            cromwell_json = cromwell_response.json()
            # Update the model with the current status
            adaptrun.status = cromwell_json["status"]
            adaptrun.save()

        # Return response with id and status
        content = {'cromwell_id': adaptrun.cromwell_id, 'status': adaptrun.status}
        return Response(content)

    def create(self, request, format=None):
        """
        Handles POST requests

        Overrides the default create function to submit to Cromwell first.
        Expects data from POST request to include the same input names as
        adapt_web.wdl. Autofills the queue and image based on our Cromwell
        server, sends the request to Cromwell, and, if successful, saves the
        run metadata in the web server database.
        """
        valid_check = self._is_valid(request)
        if not valid_check[0]:
            return valid_check[1]
        workflowInputs = {
            # Cromwell Server based inputs
            "adapt_web.adapt.queueArn": QUEUE_ARN,
            "adapt_web.adapt.image": IMAGE,
            # The objective is the only required input regardless of input type
            "adapt_web.adapt.obj": request.data['obj'],
        }
        # Add inputs if they exist
        # Cromwell requires correct typing, so cast to be safe
        for optional_input_var in BOOL_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = request.data[optional_input_var].lower() == 'true'
        for optional_input_var in STR_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = request.data[optional_input_var]
        for optional_input_var in INT_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = int(request.data[optional_input_var])
        for optional_input_var in FLOAT_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = float(request.data[optional_input_var])

        # 'Memory' is a special case; needs GB added at the end
        if 'memory' in request.data:
            workflowInputs["adapt_web.adapt.memory"] = "%sGB" %request.data['memory']

        # Files are a special case
        if 'specificity_taxa' in request.data or ('fasta[]' in request.FILES or 'specificity_fasta[]' in request.FILES):
            # If there are files in the request, upload to our S3 bucket, labeled with a unique identifier
            # We don't have Cromwell's unique identifier, so make a different one (will be stored)
            S3_id = uuid.uuid4()
            try:
                # Connect to S3 and upload file
                S3 = boto3.client("s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            except ClientError as e:
                content = {'Connection Error': "Unable to connect to our file storage. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)

            if 'specificity_taxa' in request.data:
                decoder = json.JSONDecoder()
                specificity_taxa_list = decoder.decode(request.data['specificity_taxa'])
                key = "%s/sp_tx.tsv"%(S3_id)
                sp_taxon_str = ""
                if not isinstance(specificity_taxa_list, list):
                    content = {'Input Error': "Specificity taxa not formatted correctly. "
                        "It should be a list of objects with keys of 'taxid' and optionally 'segment'"}
                    return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                for sp_tax in specificity_taxa_list:
                    if not isinstance(sp_tax, dict):
                        content = {'Input Error': "Specificity taxa not formatted correctly. "
                            "It should be a list of objects with keys of 'taxid' and optionally 'segment'"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    if 'sp_taxid' not in sp_tax:
                        content = {'Input Error': "Specificity taxa not formatted correctly. "
                            "It should be a list of objects with keys of 'taxid' and optionally 'segment'"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    if not isinstance(sp_tax['sp_taxid'], int):
                        content = {'Input Error': "Taxa in specificity taxa should be integers"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    sp_segment = sp_tax['sp_segment'] if 'sp_segment' in sp_tax else 'None'
                    if not isinstance(sp_segment, str):
                        content = {'Input Error': "Segments in specificity taxa should be strings"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    sp_taxon_str += "%i\t%s\n" %(sp_tax['sp_taxid'], sp_segment)
                specificity_taxa_file = sp_taxon_str.encode('utf-8')
                S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = specificity_taxa_file)
                workflowInputs["adapt_web.adapt.specificity_taxa"] = "s3://%s/%s" %(STORAGE_BUCKET, key)

            for uploaded_files_input_var in UPLOADED_FILES_INPUT_VARS:
                if uploaded_files_input_var in request.FILES:
                    input_files = []
                    uploaded_files_name = uploaded_files_input_var[:-2]
                    for i, input_file in enumerate(request.FILES.getlist(uploaded_files_input_var)):
                        if not self._check_fasta(input_file):
                            content = {'Input Error': "Please only select FASTAs for input files."}
                            return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                        key = "%s/%s_%i_%s"%(S3_id, uploaded_files_name, i, _format(input_file.name))
                        S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = input_file)
                        input_files.append("s3://%s/%s" %(STORAGE_BUCKET, key))
                    workflowInputs["adapt_web.adapt.%s" %uploaded_files_name] = input_files
                    request.data[uploaded_files_input_var] = input_files

        # Send to Cromwell; note that request requires input to be sent via "files"
        #   in order to send a JSON within a JSON
        cromwell_params = {'workflowInputs': json.dumps(workflowInputs),
                           'workflowUrl': WORKFLOW_URL}
        try:
            cromwell_response = requests.post(SERVER_URL, files=cromwell_params, verify=False)
        # TODO: Unsure if these are all the possible connection errors
        # TODO: Catch non-connection based errors; those are likely due to an input issue
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            content = {'Connection Error': "Unable to connect to our servers. "
                "Try again in a few minutes. If it still doesn't work, "
                "contact %s." %CONTACT}
            return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)

        nickname = ""
        if 'nickname' in request.data:
            nickname = request.data['nickname']

        alignment = False
        if 'write_aln' in request.data:
            alignment = request.data['write_aln'] == 'true'

        cromwell_json = cromwell_response.json()
        adaptrun_info = {
            # If Cromwell submission was unsuccessful, this will cause an error
            "cromwell_id": cromwell_json["id"],
            "form_inputs": request.data,
            "nickname": nickname,
            "alignment": alignment
        }

        # Set up and save run to the web server database
        serializer = ADAPTRunSerializer(data=adaptrun_info)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        rsp = Response(serializer.data, status=httpstatus.HTTP_201_CREATED)
        return rsp

    @action(detail=False, url_path=r'id_prefix/(?P<idprefix>[a-z0-9\-]+)/(?P<action>[a-z\_]+)')
    def id_prefix(self, request, *args, **kwargs):
        """
        Performs one of the actions below based on a run ID prefix specified in request

        Function called at the "id_prefix" API endpoint
        """
        content = None
        try:
            adaptrun = ADAPTRun.objects.get(cromwell_id__startswith=kwargs["idprefix"])
        except ADAPTRun.DoesNotExist:
            content = {'Input Error': "ID prefix '%s' does not match any IDs. "
            "Please double check your input." %kwargs["idprefix"]}
        except ADAPTRun.MultipleObjectsReturned:
            content = {'Input Error': "ID prefix '%s' matches multiple IDs. "
            "Please include more characters." %kwargs["idprefix"]}
        else:
            if kwargs["action"] == 'status':
                return self._get_status(adaptrun)
            elif kwargs["action"] == 'results':
                return self._get_results(adaptrun, 'json')
            elif kwargs["action"] == 'download':
                return self._get_results(adaptrun, 'file')
            elif kwargs["action"] == 'annotation':
                return self._get_results(adaptrun, 'ann')
            elif kwargs["action"] in ['alignment', 'alignment_summary']:
                if adaptrun.alignment:
                    if kwargs["action"] == 'alignment':
                        return self._get_results(adaptrun, 'aln')
                    return self._get_results(adaptrun, 'aln_sum')
                else:
                    content = {'Input Error': "There is no alignment for this run. "
                    "To generate an alignment, use the 'Output Alignment' setting in "
                    "the Advanced options section (Alignments can only outputted for "
                    "taxonomic ID input)."}
            elif kwargs["action"] == 'detail':
                self._get_status(adaptrun)
                return Response(ADAPTRunSerializer(adaptrun).data)
            else:
                content = {'Input Error': "Action '%s' is not a valid action. "
                "Action must be 'status', 'results', 'download', 'alignment', 'alignment_summary' or 'annotation'." %kwargs["action"]}

        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def status(self, request, *args, **kwargs):
        """
        Gets the status of the run ID specified in request

        Function called at the "status" API endpoint
        """
        adaptrun = self.get_object()
        return self._get_status(adaptrun)

    @action(detail=True)
    def results(self, request, *args, **kwargs):
        """
        Produces a JSON of the results

        Function called at the "results" API endpoint
        """
        adaptrun = self.get_object()
        response = self._get_results(adaptrun, 'json')
        return response

    @action(detail=True)
    def download(self, request, *args, **kwargs):
        """
        Produces a file of the results to download

        Makes a TSV if there is only one file and a ZIP otherwise.
        Function called at the "download" API endpoint.
        """
        adaptrun = self.get_object()
        response = self._get_results(adaptrun, 'file')
        return response

    @action(detail=True)
    def annotation(self, request, *args, **kwargs):
        """
        Produces a file of the results to download

        Makes a TSV if there is only one file and a ZIP otherwise.
        Function called at the "download" API endpoint.
        """
        adaptrun = self.get_object()
        response = self._get_results(adaptrun, 'ann')
        return response

    @action(detail=True)
    def alignment(self, request, *args, **kwargs):
        """
        Produces a file of the alignments to download

        Makes a fasta if there is only one file and a ZIP otherwise.
        Function called at the "alignment" API endpoint.
        """
        adaptrun = self.get_object()
        if adaptrun.alignment:
            response = self._get_results(adaptrun, 'aln')
            return response
        content = {'Input Error': "There is no alignment for this run. "
        "To generate an alignment, use the 'Output Alignment' setting in "
        "the Advanced options section (Alignments can only outputted for "
        "taxonomic ID input)."}
        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def alignment_summary(self, request, *args, **kwargs):
        """
        Produces a file of the alignments to download

        Makes a fasta if there is only one file and a ZIP otherwise.
        Function called at the "alignment" API endpoint.
        """
        adaptrun = self.get_object()
        if adaptrun.alignment:
            response = self._get_results(adaptrun, 'aln_sum')
            return response
        content = {'Input Error': "There is no alignment for this run. "
        "To generate an alignment, use the 'Output Alignment' setting in "
        "the Advanced options section (Alignments can only outputted for "
        "taxonomic ID input)."}
        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
