from django.db import models


class Virus(models.Model):
    '''Defines base model for all viruses with premade designs
    '''
    taxid = models.PositiveIntegerField(
        primary_key=True
    )
    family = models.CharField(
        max_length=100
    )
    genus = models.CharField(
        max_length=100,
        blank=True
    )
    species = models.CharField(
        max_length=100,
        blank=True
    )
    subspecies = models.CharField(
        max_length=100,
        blank=True
    )

class Primer(models.Model):
    frac_bound = models.DecimalField(
        max_digits=17,
        decimal_places=16
    )
    target = models.CharField(
        max_length = 100
    )
    start_pos = models.PositiveIntegerField()

class LeftPrimer(Primer):
    pass

class RightPrimer(Primer):
    pass

class crRNASet(models.Model):
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

class crRNA(models.Model):
    crRNA_set = models.ForeignKey(crRNASet,
        related_name='crRNAs',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    target = models.CharField(
        max_length = 100
    )
    start_pos = models.PositiveIntegerField()
    frac_bound = models.DecimalField(
        max_digits=17,
        decimal_places=16
    )
    expected_activity = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )

    # class Meta:
    #     ordering = ['crRNA_set__assay__rank', 'start_pos']

class Assay(models.Model):
    '''Defines base model for an assay for a virus
    '''
    virus = models.ForeignKey(Virus,
        related_name='assays',
        on_delete=models.CASCADE
    )
    rank = models.PositiveSmallIntegerField()
    objective_value = models.DecimalField(
        max_digits=20,
        decimal_places=16
    )
    left_primer = models.OneToOneField(
        LeftPrimer,
        on_delete=models.CASCADE
    )
    right_primer = models.OneToOneField(
        RightPrimer,
        on_delete=models.CASCADE
    )
    amplicon_start = models.PositiveIntegerField()
    amplicon_end = models.PositiveIntegerField()
    crRNA_set = models.OneToOneField(crRNASet,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['virus__taxid', 'rank']

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

    class Meta:
        ordering = ['-submit_time']

    ## Base Args
    # cromwell_id = models.CharField(
    #     max_length = 100
    # )
    # priority = models.BooleanField()


    ## Specificity
    # idm = models.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True
    # )
    # idfrac = models.DecimalField(
    #     max_digits=10,
    #     decimal_places = 9,
    #     null=True,
    #     blank=True
    # )

    # specific_against_taxa = models.CharField(
    #     blank=True
    # )
    # specific_against_fastas = models.FileField(
    #     null=True,
    #     blank=True
    # )

    ## class Meta:
    ##     abstract=True

# # Search Type
# class CompTargArgs(models.Model):
#     adaptrun = models.OneToOneField(
#         ADAPTRun,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )
#     pl = models.PositiveIntegerField(
#         null=True,
#         blank=True
#     )
#     pm = models.PositiveSmallIntegerField(
#         null=True,
#         blank=True
#     )
#     pp = models.DecimalField(
#         max_digits=10,
#         decimal_places=9,
#         null=True,
#         blank=True
#     )
#     max_primers_at_site = models.PositiveSmallIntegerField(
#         null=True,
#         blank=True
#     )
#     max_target_length = models.PositiveIntegerField(
#         null=True,
#         blank=True
#     )

# class SlidWindArgs(models.Model):
#     adaptrun = models.OneToOneField(
#         ADAPTRun,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )

#     w = models.IntegerField(
#         null=True,
#         blank=True
#     )
#     window_step = models.IntegerField(
#         null=True,
#         blank=True
#     )
#     sort = models.BooleanField(
#         null=True,
#         blank=True
#     )

# # Input Type
# class FastaArgs(model.Models):
#     adaptrun = models.OneToOneField(
#         ADAPTRun,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )

# class AutoArgArgs(model.Models):
#     adaptrun = models.OneToOneField(
#         ADAPTRun,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )
#     taxid = models.PositiveIntegerField()
#     segment = models.CharField(
#         max_length = 60,
#         blank=True
#     )
#     ref_accs = models.CharField(
#         max_length = 60,
#         blank=True
#     )

# # Objective
# class MaxActArgs(models.Model):
#     adaptrun = models.OneToOneField(
#         ADAPTRun,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )
#     soft_guide_constraint = models.PositiveSmallIntegerField(
#         null=True,
#         blank=True
#     )
#     hard_guide_constraint = models.PositiveSmallIntegerField(
#         null=True,
#         blank=True
#     )
#     penalty_strength = models.DecimalField(
#         max_digits=10,
#         decimal_places = 9,
#         null=True,
#         blank=True
#     )
#     random_greedy = models.BooleanField(
#         null=True,
#         blank=True
#     )

# class MinGuideArgs(models.Model):
#     adaptrun = models.OneToOneField(
#         ADAPTRun,
#         on_delete=models.CASCADE,
#         primary_key=True,
#     )
#     gm = models.PositiveSmallIntegerField(
#         null=True
#         blank=True
#     )
#     gp = models.DecimalField(
#         max_digits=10,
#         decimal_places=9,
#         null=True,
#         blank=True
#     )
#     required_flanking3 = models.CharField(
#         max_length = 20,
#         blank=True
#     )
#     required_flanking5 = models.CharField(
#         max_length = 20,
#         blank=True
#     )


