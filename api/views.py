import requests
import json
import zipfile
import uuid

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.core.files import File
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.reverse import reverse

from .serializers import ADAPTRunSerializer
from .models import ADAPTRun

SERVER_URL = "https://ec2-54-91-18-102.compute-1.amazonaws.com/api/workflows/v1"
WORKFLOW_URL = "https://github.com/broadinstitute/adapt-pipes/blob/master/adapt_web.wdl"
# QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/priority-Adapt-Cromwell-54-Core"
QUEUE_ARN = "none"
IMAGE = "quay.io/broadinstitute/adaptcloud"
CONTACT = "ppillai@broadinstitute.org"


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
#             return Response(content, status=status.HTTP_504_GATEWAY_TIMEOUT)
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
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            content = {'Connection Error': "Unable to connect to AWS server. "
                "Try again in a few minutes. If it still doesn't work, "
                "contact %s." %CONTACT}
            return Response(content, status=status.HTTP_504_GATEWAY_TIMEOUT)

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
            rsp = Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            rsp = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return rsp
