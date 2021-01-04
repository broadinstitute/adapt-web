import requests
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.decorators import action, api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .serializers import ADAPTRunSerializer
from .models import ADAPTRun

SERVER_URL = "https://ec2-54-91-18-102.compute-1.amazonaws.com/api/workflows/v1"
WORKFLOW_URL = "https://github.com/broadinstitute/adapt-pipes/blob/master/adapt_web.wdl"
# QUEUE_ARN = "arn:aws:batch:us-east-1:194065838422:job-queue/priority-Adapt-Cromwell-54-Core"
QUEUE_ARN = "none"
IMAGE = "quay.io/broadinstitute/adaptcloud"
CONTACT = "ppillai@broadinstitute.org"


class ADAPTRunList(APIView):
    """
    List all ADAPT runs, or create a new ADAPT run.
    """

    def get(self, request, format=None):
        adaptruns = ADAPTRun.objects.all()
        serializer = ADAPTRunSerializer(adaptruns, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        workflowInputs = {
            "adapt_web.adapt.queueArn": QUEUE_ARN,
            "adapt_web.adapt.taxid": request.data['taxid'],
            "adapt_web.adapt.segment": request.data['segment'],
            "adapt_web.adapt.obj": request.data['obj'],
            "adapt_web.adapt.specific": False,
            "adapt_web.adapt.image": IMAGE,
            "adapt_web.adapt.rand_sample": 5,
            "adapt_web.adapt.rand_seed": 294
        }

        cromwell_params = {'workflowInputs': json.dumps(workflowInputs),
                           'workflowUrl': WORKFLOW_URL}
        try:
            cromwell_response = requests.post(SERVER_URL, files=cromwell_params, verify=False)
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
            "workflowInputs": workflowInputs
        }
        # mod_request_data = request.data.copy()
        # mod_request_data.update({"cromwell_id": cromwell_json["id"]})
        serializer = ADAPTRunSerializer(data=adaptrun_info)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ADAPTRunDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an ADAPT run
    """
    queryset = ADAPTRun.objects.all()
    serializer_class = ADAPTRunSerializer


# @api_view(['GET'])
# def api_root(request, format=None):
#     return Response({
#         'ADAPT Runs': reverse('adaptrun-list', request=request, format=format),
#     })

# class ADAPTRunViewSet(viewsets.ModelViewSet):
#     queryset = ADAPTRun.objects.all().order_by('cromwell_id')
#     serializer_class = ADAPTRunSerializer

#     @action(detail=True, methods=['post'])
#     def perform_create(request):
#         """
#         Create an adapt run
#         """
#         workflowInputs = {
#             "single_adapt.adapt.queueArn": "None",
#             "single_adapt.adapt.taxid": 64320,
#             "single_adapt.adapt.ref_accs": "NC_035889",
#             "single_adapt.adapt.segment": "None",
#             "single_adapt.adapt.obj": "minimize-guides",
#             "single_adapt.adapt.specific": false,
#             "single_adapt.adapt.image": IMAGE,
#             "single_adapt.adapt.rand_sample": 5,
#             "single_adapt.adapt.rand_seed": 294
#         }
#         cromwell_params = ['workflowInputs', workflowInputs,
#                            'workflowUrl', WORKFLOW_URL]
#         cromwell_data = urllib.parse.urlencode(cromwell_params, encoding='b')
#         cromwell_request = urllib.request.request(SERVER_URL, data=cromwell_data,
#                 method='POST')
#         try:
#             cromwell_response = urlopen_with_tries(cromwell_request)
#         except (urllib.error.HTTPError, http.client.HTTPException,
#                 urllib.error.URLError, socket.timeout):
#             content = {'Connection Error': "Unable to connect to AWS server. "
#                 "Try again in a few minutes. If it still doesn't work, "
#                 "contact ppillai@broadinstitute.org."}
#             return Response(content, status=status.HTTP_504_GATEWAY_TIMEOUT)
#         cromwell_json = json.load(cromwell_response)
#         request.data.update({"cromwell_id": cromwell_json["id"]})
#         serializer = ADAPTRunSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def perform_create(self, serializer)
    #     serializer.save(owner=self.request.user)
    #     adaptruns = ADAPTRun.objects.all()
    #     serializer = ADAPTRunSerializer(adaptruns, many=True)
    #     return Response(serializer.data)
