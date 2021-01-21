import requests
import json
import zipfile
import uuid
import boto3
from io import BytesIO
from botocore.exceptions import ClientError
import sys

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, generics, mixins
from rest_framework.views import APIView
from rest_framework import status as httpstatus
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .serializers import ADAPTRunSerializer
from .models import ADAPTRun

SERVER_URL = "https://ec2-54-91-18-102.compute-1.amazonaws.com/api/workflows/v1"
WORKFLOW_URL = "https://raw.githubusercontent.com/broadinstitute/adapt-pipes/master/adapt_web.wdl"

# QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/default-Adapt-Cromwell-54-Core"
QUEUE_ARN = "none"
IMAGE = "quay.io/broadinstitute/adaptcloud"
STORAGE_BUCKET = "adaptwebstorage"

with open('./api/aws_config.txt') as f:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = f.read().splitlines()

CONTACT = "ppillai@broadinstitute.org"
SUCCESSFUL_STATES = ["Succeeded"]
FAILED_STATES = ["Failed", "Aborted"]
FINAL_STATES = SUCCESSFUL_STATES + FAILED_STATES
STR_OPT_INPUT_VARS = ['segment', 'obj']
INT_OPT_INPUT_VARS = ['taxid']
OPTIONAL_INPUT_VARS = STR_OPT_INPUT_VARS + INT_OPT_INPUT_VARS


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'adaptruns': reverse('adaptrun-list', request=request, format=format),
    })

class ADAPTRunViewSet(viewsets.ModelViewSet):
    # queryset = ADAPTRun.objects.all().order_by('cromwell_id')
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = ADAPTRun.objects.all()
    serializer_class = ADAPTRunSerializer

    def create(self, request, format=None):
        workflowInputs = {
            "adapt_web.adapt.queueArn": QUEUE_ARN,
            "adapt_web.adapt.specific": False,
            "adapt_web.adapt.image": IMAGE,
            "adapt_web.adapt.rand_sample": 5,
            "adapt_web.adapt.rand_seed": 294,
        }
        for optional_input_var in OPTIONAL_INPUT_VARS:
            if optional_input_var in request.data:
                val = request.data[optional_input_var]
                if optional_input_var in INT_OPT_INPUT_VARS:
                    val = int(val)
                workflowInputs["adapt_web.adapt.%s" %optional_input_var] = val

        if 'fasta[]' in request.FILES:
            try:
                S3 = boto3.client("s3",
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                S3_id = uuid.uuid4()
                input_files = []
                for i, input_file in enumerate(request.FILES.getlist('fasta[]')):
                    # TODO more file validation
                    if input_file.name[-6:] != ".fasta":
                        content = {'Input Error': "Please only select FASTA files as input."}
                        return Response(content, status=httpstatus.HTTP_400_BAD_REQUEST)
                    key = "%s/input%i_%s"%(S3_id, i, input_file.name)
                    S3.put_object(Bucket = STORAGE_BUCKET, Key = key, Body = input_file)
                    input_files.append("s3://%s/%s" %(STORAGE_BUCKET, key))
                workflowInputs["adapt_web.adapt.fasta"] = input_files
            except ClientError as e:
                content = {'Connection Error': "Unable to connect to our file storage. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)

        cromwell_params = {'workflowInputs': json.dumps(workflowInputs),
                           'workflowUrl': WORKFLOW_URL}
        try:
            cromwell_response = requests.post(SERVER_URL, files=cromwell_params, verify=False)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            content = {'Connection Error': "Unable to connect to our servers. "
                "Try again in a few minutes. If it still doesn't work, "
                "contact %s." %CONTACT}
            return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)

        cromwell_json = cromwell_response.json()
        del workflowInputs["adapt_web.adapt.queueArn"]
        adaptrun_info = {
            "cromwell_id": cromwell_json["id"],
            "workflowInputs": workflowInputs,
        }

        serializer = ADAPTRunSerializer(data=adaptrun_info)
        if serializer.is_valid():
            serializer.save()
            rsp = Response(serializer.data, status=httpstatus.HTTP_201_CREATED)
        else:
            rsp = Response(serializer.errors, status=httpstatus.HTTP_400_BAD_REQUEST)
        return rsp

    @action(detail=True)
    def status(self, request, *args, **kwargs):
        adaptrun = self.get_object()
        if adaptrun.status not in FINAL_STATES:
            try:
                cromwell_response = requests.get("%s/%s/status" %(SERVER_URL,adaptrun.cromwell_id), verify=False)
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
                content = {'Connection Error': "Unable to connect to our servers. "
                    "Try again in a few minutes. If it still doesn't work, "
                    "contact %s." %CONTACT}
                return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)
            cromwell_json = cromwell_response.json()
            adaptrun.status = cromwell_json["status"]
            adaptrun.save()

        content = {'cromwell_id': adaptrun.cromwell_id, 'status': adaptrun.status}
        return Response(content)


    def _getresults(self, request, *args, **kwargs):
        self.status(request, *args, **kwargs)
        adaptrun = self.get_object()
        output_files = []
        if adaptrun.status in SUCCESSFUL_STATES:
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

    @action(detail=True)
    def download(self, request, *args, **kwargs):
        response = self._getresults(request, *args, **kwargs)
        if isinstance(response, list):
            if len(response) == 1:
                output = response[0].read().decode("utf-8")
                output_type = "text/tsv"
                output_ext = ".tsv"
            else:
                output_files = [output_file.read().decode("utf-8") for output_file in response]
                output_type = "application/zip"
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

    @action(detail=True)
    def results(self, request, *args, **kwargs):
        response = self._getresults(request, *args, **kwargs)
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
