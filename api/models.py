from django.db import models

class Taxon(models.Model):
    '''Defines base model for all viral taxonomies with premade designs
    '''
    taxid = models.PositiveIntegerField(
        primary_key=True
    )


class Family(models.Model):
    '''Defines base model for all viral families with premade designs
    '''
    taxon = models.OneToOneField(Taxon,
        on_delete=models.CASCADE,
        primary_key=True
    )
    latin_name = models.CharField(
        max_length=100
    )

    @property
    def lineage(self):
        node = self
        line = []
        line.append(node)
        while hasattr(node, parent):
            node = node.parent
            line.append(node)
        return line


class Genus(models.Model):
    '''Defines base model for all viral genuses with premade designs
    '''
    taxon = models.OneToOneField(Taxon,
        on_delete=models.CASCADE,
        primary_key=True
    )
    parent = models.ForeignKey(Taxon,
        on_delete=models.CASCADE,
        related_name="genus_children"
    )
    latin_name = models.CharField(
        max_length=100,
        blank=True
    )

    @property
    def lineage(self):
        node = self
        line = []
        line.append(node)
        while hasattr(node, parent):
            node = node.parent
            line.append(node)
        return line


class Species(models.Model):
    '''Defines base model for all viral species with premade designs
    '''
    taxon = models.OneToOneField(Taxon,
        on_delete=models.CASCADE,
        primary_key=True
    )
    parent = models.ForeignKey(Taxon,
        on_delete=models.CASCADE,
        related_name="species_children"
    )
    latin_name = models.CharField(
        max_length=300,
        blank=True
    )

    @property
    def lineage(self):
        node = self
        line = []
        line.append(node)
        while hasattr(node, parent):
            node = node.parent
            line.append(node)
        return line


class Subspecies(models.Model):
    '''Defines base model for all viral subspecies with premade designs
    '''
    taxon = models.OneToOneField(Taxon,
        on_delete=models.CASCADE,
        primary_key=True
    )
    parent = models.ForeignKey(Taxon,
        on_delete=models.CASCADE,
        related_name="subspecies_children"
    )
    latin_name = models.CharField(
        max_length=300,
        blank=True
    )

    @property
    def lineage(self):
        node = self
        line = []
        line.append(node)
        while hasattr(node, parent):
            node = node.parent
            line.append(node)
        return line


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


class Assay(models.Model):
    '''Defines base model for an assay for a virus
    '''
    OBJ_CHOICES = [
        ('maximize-activity', 'maximize-activity'),
        ('minimize-guides', 'minimize-guides'),
    ]
    taxon = models.ForeignKey(Taxon,
        related_name='assays',
        on_delete=models.CASCADE
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
    created = models.DateField()
    specific = models.BooleanField()
    objective = models.CharField(
        max_length=17,
        choices=OBJ_CHOICES,
    )

    class Meta:
        ordering = ['taxon__taxid', 'rank']


class ADAPTRun(models.Model):
    '''Defines base model for all ADAPT run types
    '''
    cromwell_id = models.CharField(
        max_length=100,
        primary_key=True
    )
    workflowInputs = models.JSONField()
    status = models.CharField(
        max_length=100,
        default="Submitted"
    )
    submit_time = models.DateTimeField(
        auto_now_add=True
    )
    @property
    def short_id(self):
        return self.cromwell_id[:8]
    class Meta:
        ordering = ['-submit_time']
