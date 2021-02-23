from django.contrib import admin
from . import models

for model_name in dir(models):
    model = models.__dict__[model_name]
    if isinstance(model, type):
        admin.site.register(model)
