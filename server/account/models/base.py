from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(null=True, default=None)
    created_by = models.CharField(max_length=200, blank=True)
    updated_by = models.CharField(max_length=200, blank=True)
    deleted_by = models.CharField(max_length=200, blank=True)

    class Meta:
        abstract = True
