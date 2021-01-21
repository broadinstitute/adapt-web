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
        max_length=100
    )
    species = models.CharField(
        max_length=100
    )
    subspecies = models.CharField(
        max_length=100,
        blank=True
    )

class Assay(models.Model):
    '''Defines base model for an assay for a virus
    '''
    virus = models.ForeignKey(Virus,
        on_delete=models.CASCADE
    )
    rank = models.PositiveSmallIntegerField(
        primary_key=True
    )
    # objective_value =
    # target_start =
    # target_end =
    # target_length =
    # left_primer_start =
    # left_primer_num_primers =
    # left_primer_frac_bound =
    # left_primer_target_sequences =
    # right_primer_start =
    # right_primer_num_primers =
    # right_primer_frac_bound =
    # right_primer_target_sequences =
    # num_guides =
    # total_frac_bound_by_guides =
    # guide_set_expected_activity =
    # guide_set_median_activity =
    # guide_set_5th_pctile_activity =
    # guide_expected_activities =
    # guide_target_sequences =
    # guide_target_sequence_positions =

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


