from rest_framework import serializers
from .models import *


class ADAPTRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ADAPTRun
        fields = ('cromwell_id', 'workflowInputs', 'status', 'submit_time')

class VirusSerializer(serializers.HyperlinkedModelSerializer):
    assays = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='assay-detail'
    )
    class Meta:
        model = Virus
        fields = ('taxid', 'family', 'genus', 'species', 'subspecies', 'assays')

class AssaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Assay
        fields = ('virus', 'rank', 'objective_value', 'left_primer', 'right_primer', 'amplicon_start', 'amplicon_end', 'crRNA_set')

class crRNASetSerializer(serializers.HyperlinkedModelSerializer):
    assay = serializers.HyperlinkedRelatedField(
        view_name='assay-detail',
        read_only=True
    )
    crRNAs = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='crrna-detail'
    )
    class Meta:
        model = crRNASet
        fields = ('assay', 'frac_bound', 'expected_activity', 'median_activity', 'fifth_pctile_activity', 'crRNAs')

class crRNASerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = crRNA
        fields = ('crRNA_set', 'target', 'start_pos', 'frac_bound', 'expected_activity')

class LeftPrimerSerializer(serializers.HyperlinkedModelSerializer):
    assay = serializers.HyperlinkedRelatedField(
        view_name='assay-detail',
        read_only=True
    )
    class Meta:
        model = LeftPrimer
        fields = ('frac_bound', 'target', 'start_pos', 'assay')

class RightPrimerSerializer(serializers.HyperlinkedModelSerializer):
    assay = serializers.HyperlinkedRelatedField(
        view_name='assay-detail',
        read_only=True
    )
    class Meta:
        model = RightPrimer
        fields = ('frac_bound', 'target', 'start_pos', 'assay')
