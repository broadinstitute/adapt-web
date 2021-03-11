from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class FamilySerializer(serializers.ModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Family
        fields = ('taxon', 'latin_name')


class GenusSerializer(serializers.HyperlinkedModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Genus
        fields = ('taxon', 'parent', 'latin_name')


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Species
        fields = ('taxon', 'parent', 'latin_name')


class SubspeciesSerializer(serializers.HyperlinkedModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Subspecies
        fields = ('taxon', 'parent', 'latin_name')


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
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Assay
        fields = ('taxon', 'rank', 'objective_value', 'left_primers', 'right_primers', 'amplicon_start', 'amplicon_end', 'guide_set', 'created', 'specific', 'objective')

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


class TaxonSerializer(serializers.ModelSerializer):
    assays = AssaySerializer(
        many=True,
        read_only=True
    )
    family = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Family.objects.all(),
        allow_null=True,
        required=False
    )
    genus = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Genus.objects.all(),
        allow_null=True,
        required=False
    )
    species = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Species.objects.all(),
        allow_null=True,
        required=False
    )
    subspecies = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Subspecies.objects.all(),
        allow_null=True,
        required=False
    )
    class Meta:
        model = Taxon
        fields = ('taxid', 'family', 'genus', 'species', 'subspecies', 'assays')


class ADAPTRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ADAPTRun
        fields = ('cromwell_id', 'workflowInputs', 'status', 'submit_time')
