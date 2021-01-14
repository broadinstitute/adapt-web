import requests
import json
import zipfile
import uuid
import boto3
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
WORKFLOW_URL = "https://github.com/broadinstitute/adapt-pipes/blob/master/adapt_web.wdl"

# QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/priority-Adapt-Cromwell-54-Core"
QUEUE_ARN = "none"
IMAGE = "quay.io/broadinstitute/adaptcloud"

with open('./api/aws_config.txt') as f:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = f.read().splitlines()

CONTACT = "ppillai@broadinstitute.org"
SUCCESSFUL_STATES = ["Succeeded"]
FAILED_STATES = ["Failed", "Aborted"]
FINAL_STATES = SUCCESSFUL_STATES + FAILED_STATES


# class ADAPTRunList(generics.ListCreateAPIView):
#     """
#     List all ADAPT runs, or create a new ADAPT run.
#     """
#     queryset = ADAPTRun.objects.all()
#     serializer_class = ADAPTRunSerializer

#     def post(self, request, format=None):
#         workflowInputs = {
#             "adapt_web.adapt.queueArn": QUEUE_ARN,
#             "adapt_web.adapt.taxid": request.data['taxid'],
#             "adapt_web.adapt.segment": request.data['segment'],
#             "adapt_web.adapt.obj": request.data['obj'],
#             "adapt_web.adapt.specific": False,
#             "adapt_web.adapt.image": IMAGE,
#             "adapt_web.adapt.rand_sample": 5,
#             "adapt_web.adapt.rand_seed": 294
#         }

#         cromwell_params = {'workflowInputs': json.dumps(workflowInputs),
#                            'workflowUrl': WORKFLOW_URL}
#         try:
#             cromwell_response = requests.post(SERVER_URL, files=cromwell_params, verify=False)
#         except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
#                 requests.exceptions.Timeout):
#             content = {'Connection Error': "Unable to connect to AWS server. "
#                 "Try again in a few minutes. If it still doesn't work, "
#                 "contact %s." %CONTACT}
#             return Response(content, status=httpstatus.HTTP_504_GATEWAY_TIMEOUT)
#         cromwell_json = cromwell_response.json()
#         del workflowInputs["adapt_web.adapt.queueArn"]
#         adaptrun_info = {
#             "cromwell_id": cromwell_json["id"],
#             "workflowInputs": workflowInputs
#         }
#         # mod_request_data = request.data.copy()
#         # mod_request_data.update({"cromwell_id": cromwell_json["id"]})
#         serializer = ADAPTRunSerializer(data=adaptrun_info)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=httpstatus.HTTP_201_CREATED)
#         return Response(serializer.errors, status=httpstatus.HTTP_400_BAD_REQUEST)

# class ADAPTRunDetail(generics.RetrieveUpdateDestroyAPIView):
#     """
#     Retrieve, update or delete an ADAPT run
#     """
#     queryset = ADAPTRun.objects.all()
#     serializer_class = ADAPTRunSerializer


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
            "adapt_web.adapt.taxid": request.data['taxid'],
            "adapt_web.adapt.segment": request.data['segment'],
            "adapt_web.adapt.obj": request.data['obj'],
            "adapt_web.adapt.specific": False,
            "adapt_web.adapt.image": IMAGE,
            "adapt_web.adapt.rand_sample": 5,
            "adapt_web.adapt.rand_seed": 294,
        }
        zipfasta_rb = None
        zipfasta_f = None
        cromwell_params = {'workflowInputs': json.dumps(workflowInputs),
                           'workflowUrl': WORKFLOW_URL}
        # TODO Handle multiple files
        if 'fasta' in request.FILES:
            zipfasta_name = "%s.zip" %uuid.uuid4()
            with zipfile.ZipFile(zipfasta_name, 'w') as zipfasta_w:
                #add fastas to zipfasta
                zipfasta_w.writestr("input.fasta", request.FILES['fasta'].read())

            zipfasta_rb = open(zipfasta_name, 'rb')
            cromwell_params['workflowDependencies'] = zipfasta_rb
            zipfasta_f = File(zipfasta_rb)

            workflowInputs["adapt_web.adapt.fasta"] = "input.fasta"

        try:
            cromwell_response = requests.post(SERVER_URL, files=cromwell_params, verify=False)
        # TODO handle if fasta is too big for cromwell
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
            "zipfasta": zipfasta_f
        }

        serializer = ADAPTRunSerializer(data=adaptrun_info)
        if serializer.is_valid():
            serializer.save()
            if zipfasta_rb:
                zipfasta_rb.close()
            rsp = Response(serializer.data, status=httpstatus.HTTP_201_CREATED)
        else:
            print(serializer.errors)
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

    @action(detail=True)
    def outputs(self, request, *args, **kwargs):
        self.status(request, *args, **kwargs)
        adaptrun = self.get_object()
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
            output_files = []
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
            if len(output_files) == 1:
                final_output = list(output_files)[0]
                final_output_type = "text/csv"
            else:
                content = {'Not implemented error': "Not implemented"}
                return Response(content, status=httpstatus.HTTP_501_NOT_IMPLEMENTED)
                # with zipfile.ZipFile(, 'w')

                # # Reset file pointer
                # tmp.seek(0)
                # final_output = zipfile.ZipFile()
                # # Write file data to response
                # return HttpResponse(, mimetype='application/x-zip-compressed')
                # final_output_type = "application/zip"
            response = FileResponse(final_output, content_type=final_output_type)
            # response['Content-Length'] = final_output.size
            # response['Content-Disposition'] = 'attachment; filename="%s"' % final_output.name
            return response

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
