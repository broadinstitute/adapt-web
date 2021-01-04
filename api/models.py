from django.db import models

class ADAPTRun(models.Model):
    '''Defines base model for all ADAPT run types
    '''
    cromwell_id = models.CharField(max_length = 100)
    workflowInputs = models.JSONField()

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
    #     null=True,
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


