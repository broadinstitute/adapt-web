from rest_framework import serializers

from .models import ADAPTRun

class ADAPTRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ADAPTRun
        fields = ('id', 'cromwell_id', 'workflowInputs', 'zipfasta')
