from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class TaxonRankSerializer(serializers.ModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all(),
        allow_null=True,
        required=False
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=TaxonRank.objects.all(),
        allow_null=True,
        required=False
    )
    class Meta:
        model = TaxonRank
        fields = ('pk', 'taxon', 'latin_name', 'rank', 'parent', 'num_children', 'description', 'any_assays')


class PrimerSerializer(serializers.ModelSerializer):
    left_primer_set = serializers.PrimaryKeyRelatedField(
        queryset=LeftPrimers.objects.all(),
        allow_null=True,
        required=False
    )
    right_primer_set = serializers.PrimaryKeyRelatedField(
        queryset=RightPrimers.objects.all(),
        allow_null=True,
        required=False
    )
    class Meta:
        model = Primer
        fields = ('target', 'left_primer_set', 'right_primer_set')


class LeftPrimersSerializer(serializers.ModelSerializer):
    primers = PrimerSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = LeftPrimers
        fields = ('pk', 'frac_bound', 'start_pos', 'primers')


class RightPrimersSerializer(serializers.ModelSerializer):
    primers = PrimerSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = RightPrimers
        fields = ('pk', 'frac_bound', 'start_pos', 'primers')


class GuideSerializer(serializers.ModelSerializer):
    guide_set = serializers.PrimaryKeyRelatedField(
        queryset=GuideSet.objects.all()
    )
    class Meta:
        model = Guide
        fields = ('guide_set', 'start_pos', 'expected_activity', 'target')


class GuideSetSerializer(serializers.ModelSerializer):
    guides = GuideSerializer(
        many=True,
        read_only=True,
    )
    class Meta:
        model = GuideSet
        fields = ('pk', 'frac_bound', 'expected_activity', 'median_activity', 'fifth_pctile_activity', 'guides')


class AssaySerializer(serializers.ModelSerializer):
    left_primers = LeftPrimersSerializer()
    right_primers = RightPrimersSerializer()
    guide_set = GuideSetSerializer()
    assay_set = serializers.PrimaryKeyRelatedField(
        queryset=AssaySet.objects.all(),
        allow_null=True,
        required=False
    )
    class Meta:
        model = Assay
        fields = ('assay_set', 'rank', 'objective_value', 'left_primers', 'right_primers', 'amplicon_start', 'amplicon_end', 'guide_set')

    def create(self, validated_data):
        left_primers_data = validated_data.pop('left_primers')
        right_primers_data = validated_data.pop('right_primers')
        guide_set_data = validated_data.pop('guide_set')

        left_primers = LeftPrimers.objects.create(**left_primers_data)
        right_primers = RightPrimers.objects.create(**right_primers_data)
        guide_set = GuideSet.objects.create(**guide_set_data)

        assay = Assay.objects.create(left_primers=left_primers, right_primers=right_primers,
            guide_set=guide_set, **validated_data)

        return assay


class AssaySetSerializer(serializers.ModelSerializer):
    assays = AssaySerializer(
        many=True,
        read_only=True,
    )
    taxonrank = serializers.PrimaryKeyRelatedField(
        queryset=TaxonRank.objects.all(),
        allow_null=True,
        required=False
    )
    class Meta:
        model = AssaySet
        fields = ('pk', 'taxonrank', 'cluster',  'created', 'specific', 'objective', 'assays')


class TaxonSerializer(serializers.ModelSerializer):
    taxonrank = TaxonRankSerializer()
    class Meta:
        model = Taxon
        fields = ('taxid', 'taxonrank')

    def create(self, validated_data):
        taxonrank_data = validated_data.pop('taxonrank')
        try:
            taxonrank = TaxonRank.objects.get(latin_name=taxonrank_data['latin_name'], rank=taxonrank_data['rank'])
        except TaxonRank.DoesNotExist:
            taxonrank = TaxonRank.objects.create(**taxonrank_data)

        taxon = Taxon.objects.create(taxonrank=taxonrank, **validated_data)

        return taxon


class ADAPTRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ADAPTRun
        fields = ('cromwell_id', 'nickname', 'form_inputs', 'status', 'alignment', 'submit_time')
