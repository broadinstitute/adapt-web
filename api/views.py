import requests
import json
import zipfile
import uuid
import boto3
import sys
from io import BytesIO
from botocore.exceptions import ClientError

from django.shortcuts import render
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

SERVER_URL = "https://ip-10-0-16-250.ec2.internal/api/workflows/v1"
WORKFLOW_URL = "https://raw.githubusercontent.com/broadinstitute/adapt-pipes/main/adapt_web.wdl"

QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/default-Adapt-Cromwell-54-Core"
IMAGE = "quay.io/broadinstitute/adaptcloud"
STORAGE_BUCKET = "adaptwebstorage"

with open('./api/aws_config.txt') as f:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = f.read().splitlines()

CONTACT = "ppillai@broadinstitute.org"
SUCCESSFUL_STATES = ["Succeeded"]
FAILED_STATES = ["Failed", "Aborted"]
FINAL_STATES = SUCCESSFUL_STATES + FAILED_STATES
STR_OPT_INPUT_VARS = [
    'segment',
    'maximization_algorithm',
    'require_flanking3',
    'require_flanking5'
]
INT_OPT_INPUT_VARS = [
    'taxid',
    'gl',
    'pl',
    'pm',
    'bestntargets',
    'max_primers_at_site',
    'max_target_length',
    'idm',
    'gm',
    'soft_guide_constraint',
    'hard_guide_constraint',
    'rand_sample',
    'rand_seed',
]
FLOAT_OPT_INPUT_VARS = [
    'pp',
    'primer_gc_lo',
    'primer_gc_hi',
    'objfnweights_a',
    'objfnweights_b',
    'cluster_threshold',
    'idfrac',
    'gp',
    'penalty_strength',
]
OPTIONAL_INPUT_VARS = STR_OPT_INPUT_VARS + INT_OPT_INPUT_VARS + FLOAT_OPT_INPUT_VARS


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
    queryset = Taxon.objects.all()
    serializer_class = TaxonSerializer


class FamilyViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Family Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = Family.objects.all()
    serializer_class = FamilySerializer


class GenusViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Genus Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = GenusSerializer

    def get_queryset(self):
        family = self.request.query_params.get('family')
        if not family:
            return Genus.objects.all()
        return Genus.objects.filter(family__taxon__taxid=family)


class SpeciesViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Species Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = SpeciesSerializer

    def get_queryset(self):
        genus = self.request.query_params.get('genus')
        if not genus:
            return Species.objects.all()
        return Species.objects.filter(genus__taxon__taxid=genus)


class SubspeciesViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Subspecies Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = SubspeciesSerializer

    def get_queryset(self):
        species = self.request.query_params.get('species')
        if not species:
            return Subspecies.objects.all()
        return Subspecies.objects.filter(species__taxon__taxid=species)


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


class crRNASetViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the crRNA Set Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = crRNASet.objects.all()
    serializer_class = crRNASetSerializer


class crRNAViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the crRNA Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    queryset = crRNA.objects.all()
    serializer_class = crRNASerializer


class AssayViewSet(viewsets.ModelViewSet):
    """
    Produces the various API views for the Assay Model

    Abstracts the HTTP requests to the actions list, create, retrieve,
    update, partial_update, and destroy, which are inherited.
    """
    # These permission classes make sure only authenticated admin users can
    # edit this model
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    serializer_class = AssaySerializer
    queryset = Assay.objects.all()


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

    def _getresults(self, request, *args, **kwargs):
        """
        Helper function for download and results
        """
        # Check status of run
        self.status(request, *args, **kwargs)
        adaptrun = self.get_object()
        output_files = []
        # Only get results if job succeeded
        if adaptrun.status in SUCCESSFUL_STATES:
            # Call Cromwell server
            try:
                cromwell_response = requests.get("%s/%s/outputs" %(SERVER_URL,adaptrun.cromwell_id), verify=False)
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
                content = {'Connection Error': "Unable to connect to our servers. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)
            cromwell_json = cromwell_response.json()
            try:
                # in outputs, there should just be 1 output variable (<wdl name>.guides),
                # which contains a dictionary of key file number, value file
                S3 = boto3.client("s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                s3_file_paths = list(cromwell_json["outputs"].values())[0]
                for s3_file_path in s3_file_paths:
                    if s3_file_path[:5] == "s3://":
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

        elif adaptrun.status in FAILED_STATES:
            # TODO give reasons that the job might fail
            content = {'Bad Request': "Job has failed. "
                "This is likely due to invalid input parameters; "
                "please check your input prior to your next request. "
                "If you continue to have issues, contact %s" %CONTACT}
            return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

        else:
            content = {'Bad Request': "Job is not finished running. "
                "Please wait until the job is done; this can take a few "
                "hours on large datasets. You may check your job status "
                "at the status API endpoint."}
            return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)

        return output_files

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
        # If there are files in the request, upload to our S3 bucket, labeled with a unique identifier
        # We don't have Cromwell's unique identifier, so make a different one (will be stored)
        S3_id = uuid.uuid4()
        if 'fasta[]' in request.FILES:
            try:
                # Connect to S3 and upload file
                S3 = boto3.client("s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                input_files = []
                for i, input_file in enumerate(request.FILES.getlist('fasta[]')):
                    # TODO more file validation
                    if input_file.name[-6:] != ".fasta":
                        content = {'Input Error': "Please only select FASTA files as input."}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    key = "%s/in_%i_%s"%(S3_id, i, input_file.name)
                    S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = input_file)
                    input_files.append("s3://%s/%s" %(STORAGE_BUCKET, key))
                workflowInputs["adapt_web.adapt.fasta"] = input_files
            except ClientError as e:
                # TODO: could add more specific errors?
                content = {'Connection Error': "Unable to connect to our file storage. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)

        # TODO: deduplicate this code; nearly identical to above
        if 'specificity_fasta[]' in request.FILES:
            try:
                S3 = boto3.client("s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                sp_files = []
                for i, sp_file in enumerate(request.FILES.getlist('specificity_fasta[]')):
                    # TODO more file validation
                    if sp_file.name[-6:] != ".fasta":
                        content = {'Input Error': "Please only select FASTA files as input."}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    key = "%s/sp_%i_%s"%(S3_id, i, sp_file.name)
                    S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = sp_file)
                    sp_files.append("s3://%s/%s" %(STORAGE_BUCKET, key))
                workflowInputs["adapt_web.adapt.specificity_fasta"] = sp_files
            except ClientError as e:
                content = {'Connection Error': "Unable to connect to our file storage. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)

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
        # Don't store confidential information on our AWS account in the web server database;
        # do store the cromwell ID
        del workflowInputs["adapt_web.adapt.queueArn"]
        adaptrun_info = {
            # If Cromwell submission was unsuccessful, this will cause an error
            "cromwell_id": cromwell_json["id"],
            "workflowInputs": workflowInputs,
        }

        # Set up and save run to the web server database
        serializer = ADAPTRunSerializer(data=adaptrun_info)
        if serializer.is_valid():
            serializer.save()
            rsp = Response(serializer.data, status=httpstatus.HTTP_201_CREATED)
        else:
            # This should never happen, since the inputs are set only after a
            # successful submission to Cromwell
            rsp = Response(serializer.errors, status=httpstatus.HTTP_400_BAD_REQUEST)
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
                    content[i][j] = {headers[k]: val for k,val in enumerate(line.split('\t'))}
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
