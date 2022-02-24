from django.db import models


class TaxonRank(models.Model):
    '''Defines base model for all viral genuses with premade designs
    '''
    RANK_CHOICES = [
        ('family', 'family'),
        ('genus', 'genus'),
        ('species', 'species'),
        ('subspecies', 'subspecies'),
        ('segment', 'segment'),
    ]
    parent = models.ForeignKey('self',
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True
    )
    latin_name = models.CharField(
        max_length=100
    )
    rank = models.CharField(
        max_length=10,
        choices=RANK_CHOICES,
    )
    description = models.TextField(
        blank=True
    )

    @property
    def num_segments(self):
        return len(self.children.filter(rank="segment"))

    @property
    def parent_info(self):
        if self.parent:
            taxids = [taxon.taxid for taxon in self.parent.taxons.all()]
            return [self.parent.rank, self.parent.latin_name, taxids]
        else:
            return None

    @property
    def num_children(self):
        return len(self.children.all())

    @property
    def any_assays(self):
        return self.assay_sets.all().exists()

    @property
    def any_child_assays(self):
        children = self.children.all()
        while len(children) > 0:
            child = children.pop(0)
            if child.any_assays():
                return True
            children.append(child.children.all())
        return self.assay_sets.all().exists()

    class Meta:
        ordering = ['rank', 'latin_name']


class Taxon(models.Model):
    '''Defines base model for all viral taxonomies with premade designs
    '''
    taxid = models.PositiveIntegerField(
        primary_key=True
    )
    taxonrank = models.ForeignKey(TaxonRank,
        related_name='taxons',
        on_delete=models.CASCADE
    )


class PrimerSet(models.Model):
    frac_bound = models.DecimalField(
        max_digits=17,
        decimal_places=16
    )
    start_pos = models.PositiveIntegerField()


class LeftPrimers(PrimerSet):
    pass


class RightPrimers(PrimerSet):
    pass


class Primer(models.Model):
    target = models.CharField(
        max_length = 100
    )
    left_primer_set = models.ForeignKey(LeftPrimers,
        related_name='primers',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    right_primer_set = models.ForeignKey(RightPrimers,
        related_name='primers',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )


class GuideSet(models.Model):
    frac_bound = models.DecimalField(
        max_digits=17,
        decimal_places=16
    )
    expected_activity = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )
    median_activity = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )
    fifth_pctile_activity = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )


class Guide(models.Model):
    guide_set = models.ForeignKey(GuideSet,
        related_name='guides',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target = models.CharField(
        max_length = 100
    )
    start_pos = models.JSONField()
    expected_activity = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )

    # class Meta:
    #     ordering = ['crRNA_set__assay__rank', 'start_pos']

class AssaySet(models.Model):
    '''Defines base model for an assay set for a virus
    '''
    OBJ_CHOICES = [
        ('maximize-activity', 'maximize-activity'),
        ('minimize-guides', 'minimize-guides'),
    ]
    taxonrank = models.ForeignKey(TaxonRank,
        related_name='assay_sets',
        on_delete=models.CASCADE
    )
    created = models.DateField()
    specific = models.BooleanField()
    objective = models.CharField(
        max_length=17,
        choices=OBJ_CHOICES,
    )
    cluster = models.PositiveSmallIntegerField(default=0)
    s3_aln_path = models.TextField(
        default="",
        blank=True
    )
    s3_ann_path = models.TextField(
        default="",
        blank=True
    )

class Assay(models.Model):
    '''Defines base model for an assay for a virus
    '''
    assay_set = models.ForeignKey(AssaySet,
        related_name='assays',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    rank = models.PositiveSmallIntegerField()
    objective_value = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )
    left_primers = models.OneToOneField(
        LeftPrimers,
        on_delete=models.CASCADE
    )
    right_primers = models.OneToOneField(
        RightPrimers,
        on_delete=models.CASCADE
    )
    amplicon_start = models.PositiveIntegerField()
    amplicon_end = models.PositiveIntegerField()
    guide_set = models.OneToOneField(GuideSet,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['assay_set__taxonrank__latin_name', 'assay_set__created', 'rank']


class ADAPTRun(models.Model):
    '''Defines base model for all ADAPT run types
    '''
    cromwell_id = models.CharField(
        max_length=100,
        primary_key=True
    )
    form_inputs = models.JSONField()
    status = models.CharField(
        max_length=100,
        default="Submitted"
    )
    submit_time = models.DateTimeField(
        auto_now_add=True
    )
    nickname = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )
    alignment = models.BooleanField(
        default=False
    )

    @property
    def short_id(self):
        return self.cromwell_id[:8]

    class Meta:
        ordering = ['-submit_time']
