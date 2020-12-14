from django.db import models

class ADAPTRun(models.Model):
	cromwell_id = models.CharField(max_length = 100)
	taxid = models.IntegerField()
	ref_accs = models.CharField(max_length = 60)
