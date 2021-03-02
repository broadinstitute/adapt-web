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
    class Meta:
        model = Genus
        fields = ('taxon', 'family', 'latin_name')


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Species
        fields = ('taxon', 'genus', 'latin_name', 'lineage_names')


class SubspeciesSerializer(serializers.HyperlinkedModelSerializer):
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Subspecies
        fields = ('taxon', 'species', 'latin_name', 'lineage_names')


class PrimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Primer
        fields = ('target', )


class LeftPrimersSerializer(serializers.ModelSerializer):
    primers = PrimerSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = LeftPrimers
        fields = ('frac_bound', 'start_pos', 'primers')


class RightPrimersSerializer(serializers.ModelSerializer):
    primers = PrimerSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = RightPrimers
        fields = ('frac_bound', 'start_pos', 'primers')


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
        read_only=True
    )
    assay = serializers.PrimaryKeyRelatedField(
        queryset=Assay.objects.all()
    )
    class Meta:
        model = GuideSet
        fields = ('assay', 'frac_bound', 'expected_activity', 'median_activity', 'fifth_pctile_activity', 'guides')


class AssaySerializer(serializers.ModelSerializer):
    left_primers = LeftPrimersSerializer(read_only=True)
    right_primers = RightPrimersSerializer(read_only=True)
    guide_set = GuideSetSerializer(read_only=True)
    taxon = serializers.PrimaryKeyRelatedField(
        queryset=Taxon.objects.all()
    )
    class Meta:
        model = Assay
        fields = ('taxon', 'rank', 'objective_value', 'left_primers', 'right_primers', 'amplicon_start', 'amplicon_end', 'guide_set')


class TaxonSerializer(serializers.ModelSerializer):
    assays = AssaySerializer(
        many=True,
        read_only=True
    )
    family = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Family.objects.all(),
        allow_null=True
    )
    genus = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Genus.objects.all(),
        allow_null=True
    )
    species = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Species.objects.all(),
        allow_null=True
    )
    subspecies = serializers.SlugRelatedField(
        slug_field='latin_name',
        queryset=Subspecies.objects.all(),
        allow_null=True
    )
    class Meta:
        model = Taxon
        fields = ('taxid', 'family', 'genus', 'species', 'subspecies', 'assays')


class ADAPTRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ADAPTRun
        fields = ('cromwell_id', 'workflowInputs', 'status', 'submit_time')
