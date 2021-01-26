from rest_framework import serializers
from .models import ADAPTRun, Virus


class ADAPTRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ADAPTRun
        fields = ('cromwell_id', 'workflowInputs', 'status', 'submit_time')

# class VirusSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Virus
        # fields = ('taxid', 'family', 'genus', 'species', 'subspecies')
