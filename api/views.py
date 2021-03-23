import requests
import json
import csv
import zipfile
import tempfile
import uuid
import boto3
import sys
import xml.etree.ElementTree as ET
from io import BytesIO
from botocore.exceptions import ClientError

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

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

QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/default-Adapt-Cromwell-54-Core"
IMAGE = "quay.io/broadinstitute/adaptcloud"
STORAGE_BUCKET = "adaptwebstorage"

with open('./api/aws_config.txt') as f:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = f.read().splitlines()

CONTACT = "ppillai@broadinstitute.org"
SUCCESSFUL_STATES = ["Succeeded"]
FAILED_STATES = ["Failed", "Aborted"]
OBJECTIVES = ["maximize-activity", "minimize-guides"]
MAX_ALGS = ["random-greedy", "greedy"]
FINAL_STATES = SUCCESSFUL_STATES + FAILED_STATES
VALID_BASES = {'G', 'A', 'T', 'C', 'R', 'Y', 'M', 'K', 'S', 'W', 'H', 'B', 'V', 'D', 'N'}

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
OPTIONAL_INPUT_VARS = STR_OPT_INPUT_VARS + INT_OPT_INPUT_VARS + FLOAT_OPT_INPUT_VARS
FILES_INPUT_VARS = ['fasta[]', 'sp_fasta[]', 'sp_taxa']
GL_DEFAULT = 28
PL_DEFAULT = 30
SOFT_GUIDE_DEFAULT = 1
P_GC_LO_DEFAULT = 0.35
P_GC_HI_DEFAULT = 0.65

LINEAGE_RANKS = ['family', 'genus', 'species', 'subspecies']


def _valid_genome(genome):
    for char in genome:
        if char not in VALID_BASES:
            return False
    return True


def _replace_spaces(filename):
    return filename.replace(' ', '_')


def _metadata(cromwell_id):
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

    def get_queryset(self):
        taxids = self.request.query_params.get('taxid')
        if not taxids:
            return Taxon.objects.all()
        taxids = taxids.split(',')
        taxids_qs = Taxon.objects.filter(taxid=taxids[0])
        if len(taxids) > 1:
            for taxid in parents[1:]:
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
        parents = self.request.query_params.get('parent')
        if not parents:
            return TaxonRank.objects.all()
        parents = parents.split(',')
        if parents[0] == 'null':
            parents_qs = TaxonRank.objects.filter(parent__isnull=True)
        else:
            parents_qs = TaxonRank.objects.filter(parent=parents[0])
        if len(parents) > 1:
            for parent in parents[1:]:
                if parent == 'null':
                    parents_qs = parents_qs.union(TaxonRank.objects.filter(parent__taxid__isnull=True))
                else:
                    parents_qs = parents_qs.union(TaxonRank.objects.filter(parent__taxid=parent))
        return parents_qs


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


    @action(detail=False, methods=['post'])
    def database_update(self, request, *args, **kwargs):
        """
        Updates the database given a job ID from Cromwell

        """

        # Call Cromwell server
        metadata_response = _metadata(request.data["id"])
        if isinstance(metadata_response, Response):
            return metadata_response

        # Get file paths for S3
        s3_file_paths = metadata_response["outputs"]["parallel_adapt.guides"]
        # Parse taxa information and make taxa for those that do not exist in database
        taxa_file_path = metadata_response["outputs"]["parallel_adapt.output_taxa_file"]
        start_time = metadata_response["start"][:10]
        taxa_file = _files([taxa_file_path])
        if isinstance(taxa_file, Response):
            return taxa_file
        taxa_lines = taxa_file[0].read().decode("utf-8").splitlines()
        taxa_headers = taxa_lines[0].split('\t')
        taxa = [{taxa_headers[i]: val \
            for i, val in enumerate(taxa_line.split('\t'))} \
            for taxa_line in taxa_lines[1:]]
        objs = metadata_response["inputs"]["parallel_adapt.objs"]
        sps = metadata_response["inputs"]["parallel_adapt.sps"]

        def save_by_rank(taxid, name, rank, parent=None):
            if rank not in LINEAGE_RANKS:
                raise ValueError('The rank %s is not built into the database structure' %rank)
            data = {'taxid': taxid, 'taxonrank': {'latin_name': name, 'rank': rank}}
            if parent:
                data['taxonrank']['parent'] = parent.pk
            serializer = TaxonSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            taxon = serializer.save()
            return taxon.taxonrank

        for i, sp in enumerate(sps):
            for j, obj in enumerate(objs):
                for k, taxon in enumerate(taxa):
                    try:
                        taxon_obj = get_object_or_404(Taxon, pk=int(taxon["taxid"]))
                        taxonrank_obj = taxon_obj.taxonrank
                    except Http404:
                        params = {'db': 'taxonomy', 'id': int(taxon['taxid'])}
                        tax_xml = requests.get(NCBI_URL, params=params).text
                        tax_ET = ET.fromstring(tax_xml)[0]
                        # NOTE this is based on the current model we're using in the spreadsheet.
                        # Could/should generalize spreadsheet
                        tax_name = taxon['species']
                        tax_rank = tax_ET.find('Rank').text
                        lineage = tax_ET.find('LineageEx')
                        parent = None
                        for ancestor in lineage.findall('Taxon'):
                            ancestor_id = ancestor.find('TaxId').text
                            ancestor_name = ancestor.find('ScientificName').text
                            ancestor_rank = ancestor.find('Rank').text
                            if ancestor_rank in LINEAGE_RANKS:
                                parent = save_by_rank(ancestor_id, ancestor_name, ancestor_rank, parent=parent)
                        taxonrank_obj = save_by_rank(taxon['taxid'], tax_name, tax_rank, parent=parent)
                    output_files = [output_file.read().decode("utf-8") for output_file in _files(s3_file_paths[i][j][k])]

                    for i, output_file in enumerate(output_files):
                        lines = output_file.splitlines()
                        headers = lines[0].split('\t')
                        for j, line in enumerate(lines[1:]):
                            raw_content = {headers[k]: val for k,val in enumerate(line.split('\t'))}

                            assay_data = {
                                "left_primers": {
                                    "frac_bound": float(raw_content["left-primer-frac-bound"]),
                                    "start_pos": int(raw_content["left-primer-start"])
                                },
                                "right_primers": {
                                    "frac_bound": float(raw_content["right-primer-frac-bound"]),
                                    "start_pos": int(raw_content["right-primer-start"])
                                },
                                "guide_set": {
                                    "frac_bound": float(raw_content["total-frac-bound-by-guides"]),
                                    "expected_activity": float(raw_content["guide-set-expected-activity"]),
                                    "median_activity": float(raw_content["guide-set-median-activity"]),
                                    "fifth_pctile_activity": float(raw_content["guide-set-5th-pctile-activity"])
                                },
                                'taxonrank': taxonrank_obj.pk,
                                'rank': j,
                                'cluster': i,
                                'objective_value': float(raw_content["objective-value"]),
                                'amplicon_start': int(raw_content["target-start"]),
                                'amplicon_end': int(raw_content["target-end"]),
                                'created': start_time,
                                'specific': sp,
                                'objective': obj
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

                            for k, target in enumerate(raw_content["left-primer-target-sequences"].split(" ")):
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

    def get_queryset(self):
        taxonrank = self.request.query_params.get('taxonrank')
        cluster = self.request.query_params.get('cluster')
        if taxonrank:
            if cluster:
                return Assay.objects.filter(taxonrank=taxonrank, cluster=cluster)
            else:
                return Assay.objects.filter(taxonrank=taxonrank)
        elif cluster:
            return Assay.objects.filter(cluster=cluster)
        return Assay.objects.all()



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
        filetypes = [".fasta", ".fa", ".fna", ".ffn", ".faa", ".frn", ".aln"]
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
                            "<ul><li>%s</li></ul>" %(value, '</li><li>'.join(VALID_BASES))
                        break
                elif input_var in POS_INT_OPT_INPUT_VARS:
                    if (not value.isdigit()) or value == '0':
                        content = "'%s' is invalid for %s; it must be a positive integer" %(value, _replace_spaces(input_var))
                        break
                    if input_var == 'max_target_length':
                        mod_value = int(value)
                        try:
                            gl = int(request.data['gl']) if 'gl' in request.data else GL_DEFAULT
                            pl = int(request.data['pl']) if 'pl' in request.data else PL_DEFAULT
                            if mod_value < max(gl, pl):
                                content = "'%s' is invalid for %s; it must be at least as large at the primer length and the guide length" %(value, _replace_spaces(input_var))
                                break
                        except:
                            pass
                    elif input_var == 'hard_guide_constraint':
                        mod_value = int(value)
                        try:
                            soft_guide = int(request.data['soft_guide_constraint']) if 'soft_guide_constraint' in request.data else SOFT_GUIDE_DEFAULT
                            if mod_value < soft_guide:
                                content = "'%s' is invalid for %s; it must be at least as large at the primer length and the guide length" %(value, _replace_spaces(input_var))
                                break
                        except:
                            pass
                elif input_var in NONNEG_INT_OPT_INPUT_VARS:
                    if not value.isdigit():
                        content = "'%s' is invalid for %s; it must be a nonnegative integer" %(value, _replace_spaces(input_var))
                        break
                elif input_var in FLOAT_OPT_INPUT_VARS:
                    try:
                        mod_value = float(value)
                    except:
                        content = "'%s' is invalid for %s; it must be a decimal" %(value, _replace_spaces(input_var))
                        break
                    else:
                        if mod_value < 0:
                            content = "'%s' is invalid for %s; it must be between 0 and 1 (inclusive)" %(value, _replace_spaces(input_var))
                            break
                        if input_var in FRAC_OPT_INPUT_VARS:
                            if mod_value > 1:
                                content = "'%s' is invalid for %s; it must be between 0 and 1 (inclusive)" %(value, _replace_spaces(input_var))
                                break
                        if input_var == 'primer_gc_lo':
                            try:
                                primer_gc_hi = float(request.data['primer_gc_hi']) if 'primer_gc_hi' in request.data else P_GC_HI_DEFAULT
                                if mod_value > primer_gc_hi:
                                    content = "'%s' is invalid for the lowest GC primer percent content; it must " \
                                        "be less than the highest GC primer percent content" %(value, _replace_spaces(input_var))
                                    break
                            except:
                                pass
                        elif input_var == 'primer_gc_hi':
                            try:
                                primer_gc_lo = float(request.data['primer_gc_lo']) if 'primer_gc_lo' in request.data else P_GC_LO_DEFAULT
                                if mod_value < primer_gc_lo:
                                    content = "'%s' is invalid for the highest GC primer percent content; it must " \
                                        "be greater than the lowest GC primer percent content" %(value, _replace_spaces(input_var))
                                    break
                            except:
                                pass
                elif input_var not in FILES_INPUT_VARS:
                    content = "%s is not a valid input parameter" % input_var
                    break
        if content:
            return (False, Response({'Input Error': content}, status=httpstatus.HTTP_400_BAD_REQUEST))
        return (True, )

    def _getresults(self, request, *args, **kwargs):
        """
        Helper function for download and results
        """
        # Check status of run
        self.status(request, *args, **kwargs)
        adaptrun = self.get_object()
        # Only get results if job succeeded
        if adaptrun.status in SUCCESSFUL_STATES:
            # Call Cromwell server
            metadata_response = _metadata(adaptrun.cromwell_id)
            if isinstance(metadata_response, Response):
                return metadata_response
            # Download files from S3
            return _files(metadata_response["outputs"]["adapt_web.guides"])

        elif adaptrun.status in FAILED_STATES:
            # TODO give reasons that the job might fail
            content = {'Failed Job': "Job has failed. "
                "This is likely due to invalid input parameters; "
                "please check your input prior to your next request. "
                "If you continue to have issues, contact %s" %CONTACT}
            return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

        else:
            content = {'Unfinished Job': "Job is not finished running. "
                "Please wait until the job is done; this can take a few "
                "hours on large datasets. You may check your job status "
                "using 'Get Status'."}
            return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

    def create(self, request, format=None):
        """
        Handles POST requests

        Overrides the default create function to submit to Cromwell first.
        Expects data from POST request to include the same input names as
        adapt_web.wdl. Autofills the queue and image based on our Cromwell
        server, sends the request to Cromwell, and, if successful, saves the
        run metadata in the web server database.
        """
        # TODO: Validate inputs before sending to Cromwell
        valid_check = ADAPTRunViewSet._is_valid(request)
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
        for optional_input_var in STR_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = request.data[optional_input_var]
        for optional_input_var in INT_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = int(request.data[optional_input_var])
        for optional_input_var in FLOAT_OPT_INPUT_VARS:
            if optional_input_var in request.data:
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = float(request.data[optional_input_var])

        if 'sp_taxa' in request.data or ('fasta[]' in request.FILES or 'sp_fasta[]' in request.FILES):
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

            if 'sp_taxa' in request.data:
                decoder = json.JSONDecoder()
                sp_taxa_list = decoder.decode(request.data['sp_taxa'])
                if not isinstance(sp_taxa_list, list):
                    content = {'Input Error': "Specificity taxa not formatted correctly. "
                        "It should be a list of objects with keys of 'taxid' and optionally 'segment'"}
                    return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                for sp_tax in sp_taxa_list:
                    if not isinstance(sp_tax, dict):
                        content = {'Input Error': "Specificity taxa not formatted correctly. "
                            "It should be a list of objects with keys of 'taxid' and optionally 'segment'"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    if 'taxid' not in sp_tax:
                        content = {'Input Error': "Specificity taxa not formatted correctly. "
                            "It should be a list of objects with keys of 'taxid' and optionally 'segment'"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                key = "%s/sp_tx.tsv"%(S3_id)
                sp_taxon_str = ""
                for sp_taxon in sp_taxa_list:
                    if not isinstance(sp_taxon['taxid'], str) or not sp_taxon['taxid'].isdigit():
                        content = {'Input Error': "Taxa in specificity taxa should be nonnegative integers"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    segment = sp_taxon['segment'] if sp_taxon['segment'] else 'None'
                    if not isinstance(segment, str):
                        content = {'Input Error': "Segments in specificity taxa should be strings"}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    sp_taxon_str += "%s\t%s\n" %(sp_taxon['taxid'], segment)
                sp_taxa_file = sp_taxon_str.encode('utf-8')
                S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = sp_taxa_file)
                workflowInputs["adapt_web.adapt.specificity_taxa"] = key

            if 'fasta[]' in request.FILES:
                input_files = []
                for i, input_file in enumerate(request.FILES.getlist('fasta[]')):
                    if not ADAPTRunViewSet._check_fasta(input_file):
                        content = {'Input Error': "Please only select FASTAs for input files."}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    key = "%s/in_%i_%s"%(S3_id, i, _replace_spaces(input_file.name))
                    S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = input_file)
                    input_files.append("s3://%s/%s" %(STORAGE_BUCKET, key))
                workflowInputs["adapt_web.adapt.fasta"] = input_files

            # TODO: deduplicate this code; nearly identical to above
            if 'sp_fasta[]' in request.FILES:
                sp_files = []
                for i, sp_file in enumerate(request.FILES.getlist('sp_fasta[]')):
                    if not ADAPTRunViewSet._check_fasta(sp_file):
                        content = {'Input Error': "Please only select FASTAs for specificity files."}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    key = "%s/sp_%i_%s"%(S3_id, i, _replace_spaces(sp_file.name))
                    S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = sp_file)
                    sp_files.append("s3://%s/%s" %(STORAGE_BUCKET, key))
                workflowInputs["adapt_web.adapt.specificity_fasta"] = sp_files

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

        cromwell_json = cromwell_response.json()
        adaptrun_info = {
            # If Cromwell submission was unsuccessful, this will cause an error
            "cromwell_id": cromwell_json["id"],
            "form_inputs": request.data,
        }

        # Set up and save run to the web server database
        serializer = ADAPTRunSerializer(data=adaptrun_info)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        rsp = Response(serializer.data, status=httpstatus.HTTP_201_CREATED)
        return rsp

    @action(detail=True)
    def status(self, request, *args, **kwargs):
        """
        Gets the status of the run ID specified in request

        Function called at the "status" API endpoint
        """
        adaptrun = self.get_object()
        # Check if the run wasn't finished the last time status was checked
        if adaptrun.status not in FINAL_STATES:
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

    @action(detail=True)
    def results(self, request, *args, **kwargs):
        """
        Produces a JSON of the results

        Function called at the "results" API endpoint
        """
        response = self._getresults(request, *args, **kwargs)
        # The 'response' from _getresults is either an HTTP Response
        # or a list of files which needs to be processed
        if isinstance(response, list):
            output_files = [output_file.read().decode("utf-8") for output_file in response]
            content = {}

            for i, output_file in enumerate(output_files):
                content[i] = {}
                lines = output_file.splitlines()
                headers = lines[0].split('\t')
                for j, line in enumerate(lines[1:]):
                    raw_content = {headers[k]: val for k,val in enumerate(line.split('\t'))}
                    content[i][j] = {}
                    content[i][j]["rank"] = j
                    content[i][j]["objective_value"] = float(raw_content["objective-value"])
                    content[i][j]["left_primers"] = {
                        "frac_bound": float(raw_content["left-primer-frac-bound"]),
                        "start_pos": int(raw_content["left-primer-start"])
                    }
                    content[i][j]["left_primers"]["primers"] = [
                        {
                            "target": target
                        } \
                    for target in raw_content["left-primer-target-sequences"].split(" ")]
                    content[i][j]["right_primers"] = {
                        "frac_bound": float(raw_content["right-primer-frac-bound"]),
                        "start_pos": int(raw_content["right-primer-start"])
                    }
                    content[i][j]["right_primers"]["primers"] = [
                        {
                            "target": target
                        } \
                    for target in raw_content["right-primer-target-sequences"].split(" ")]
                    content[i][j]["amplicon_start"] = int(raw_content["target-start"])
                    content[i][j]["amplicon_end"] = int(raw_content["target-end"])
                    content[i][j]["guide_set"] = {
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
                    targets = raw_content["left-primer-target-sequences"].split(" ")
                    content[i][j]["guide_set"]["guides"] = [
                        {
                            "start_pos": start_poses[k],
                            "expected_activity": expected_activities[k],
                            "target": targets[k]
                        } \
                    for k in range(len(targets))]

            response = Response(content)
        return response

    @action(detail=True)
    def download(self, request, *args, **kwargs):
        """
        Produces a file of the results to download

        Makes a TSV if there is only one file and a ZIP otherwise.
        Function called at the "download" API endpoint.
        """
        response = self._getresults(request, *args, **kwargs)
        # The 'response' from _getresults is either an HTTP Response
        # or a list of files which needs to be processed
        if isinstance(response, list):
            if len(response) == 1:
                # If there is only one file, no need to zip
                output = response[0].read().decode("utf-8")
                output_type = "text/tsv"
                output_ext = ".tsv"
            else:
                output_files = [output_file.read().decode("utf-8") for output_file in response]
                output_type = "application/zip"
                # Create the zip file in memory only
                zipped_output = BytesIO()
                with zipfile.ZipFile(zipped_output, "a", zipfile.ZIP_DEFLATED) as zipped_output_a:
                    for i, output_file in enumerate(output):
                        zipped_output_a.writestr("%s.%i.tsv" %(self.kwargs['pk'], i), output_file)
                zipped_output.seek(0)
                output = zipped_output
                output_ext = ".zip"
            filename = self.kwargs['pk']+output_ext
            response = FileResponse(output, content_type=output_type)
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
