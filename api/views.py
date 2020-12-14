import urllib.parse
import urllib.request
import http.client
import socket
import random
import time

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action, api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .serializers import ADAPTRunSerializer
from .models import ADAPTRun

SERVER_URL = "https://ec2-54-91-18-102.compute-1.amazonaws.com/api/workflows/v1"
WORKFLOW_URL = "https://github.com/broadinstitute/adapt-pipes/blob/master/single_adapt.wdl"
IMAGE = "quay.io/broadinstitute/adaptcloud",


@api_view(['GET', 'POST'])
def adaptrun_list(request, format=None):
    """
    List all ADAPT runs, or create a new ADAPT run.
    """
    if request.method == 'GET':
        adaptruns = ADAPTRun.objects.all()
        serializer = ADAPTRunSerializer(adaptruns, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        workflowInputs = {
            "single_adapt.adapt.queueArn": "None",
            "single_adapt.adapt.taxid": 64320,
            "single_adapt.adapt.ref_accs": "NC_035889",
            "single_adapt.adapt.segment": "None",
            "single_adapt.adapt.obj": "minimize-guides",
            "single_adapt.adapt.specific": "false",
            "single_adapt.adapt.image": IMAGE,
            "single_adapt.adapt.rand_sample": 5,
            "single_adapt.adapt.rand_seed": 294
        }
        cromwell_params = {'workflowInputs': workflowInputs,
                           'workflowUrl': WORKFLOW_URL}
        cromwell_data = urllib.parse.urlencode(cromwell_params)
        cromwell_data = cromwell_data.encode('ascii')
        cromwell_request = urllib.request.Request(SERVER_URL, data=cromwell_data, 
                method='POST')
        try:
            cromwell_response = urlopen_with_tries(cromwell_request)
        except (urllib.error.HTTPError, http.client.HTTPException,
                urllib.error.URLError, socket.timeout):
            content = {'Connection Error': "Unable to connect to AWS server. "
                "Try again in a few minutes. If it still doesn't work, "
                "contact ppillai@broadinstitute.org."}
            return Response(content, status=status.HTTP_504_GATEWAY_TIMEOUT)
        cromwell_json = json.load(cromwell_response)
        request.data.update({"cromwell_id": cromwell_json["id"]})
        data = JSONParser().parse(request)
        serializer = ADAPTRunSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def adaptrun_detail(request, pk, format=None):
    """
    Retrieve, update or delete an ADAPT run
    """
    try:
        adaptrun = ADAPTRun.objects.get(pk=pk)
    except ADAPTRun.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ADAPTRunSerializer(adaptrun)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ADAPTRunSerializer(adaptrun, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        adaptrun.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

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


def urlopen_with_tries(url, initial_wait=5, #rand_wait_range=(1, 30),
        max_num_tries=5, timeout=60, read=False):
    """
    Open a URL via urllib with repeated tries.

    Often calling urllib.request.urlopen() fails with HTTPError, especially
    if there are multiple processes calling it. The reason is that NCBI
    has a cap on the number of requests per unit time, and the error raised
    is 'HTTP Error 429: Too Many Requests'.

    Args:
        url: url or Request object to open
        initial_wait: number of seconds to wait in between the first two
            requests; the wait for each subsequent request doubles in time
        rand_wait_range: tuple (a, b); in addition to waiting an amount of
            time that grows exponentially (starting with initial_wait), also
            wait a random number of seconds between a and b (inclusive).
            If multiple processes are started simultaneously, this helps to
            avoid them waiting on the same cycle
        max_num_tries: maximum number of requests to attempt to make
        timeout: timeout in sec before retrying
        read: also try to read the opened URL, and return the results;
            if this raises an HTTPException, the call will be retried

    Returns:
        result of urllib.request.urlopen(); unless read is True, in which
        case it is the data returned by reading the url
    """
    num_tries = 0
    while num_tries < max_num_tries:
        try:
            num_tries += 1
            r = urllib.request.urlopen(url, timeout=timeout)
            return r
        except (urllib.error.HTTPError, http.client.HTTPException,
                urllib.error.URLError, socket.timeout):
            if num_tries == max_num_tries:
                raise
            else:
                # Pause for a bit and retry
                wait = initial_wait * 2**(num_tries - 1)
                rand_wait = 0#random.randint(*rand_wait_range)
                total_wait = wait + rand_wait
                time.sleep(total_wait)
