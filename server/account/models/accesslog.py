from django.conf import settings
from django.db import models


class AccessLogManager(models.Manager):
    def create(self, **kwargs):
        instance = super().create(**kwargs)
        created_date = instance.created.isoformat()  # YYYY-MM-DD
        instance.created_date = created_date
        instance.created_month = created_date[:-3]  # YYYY-MM
        instance.save()
        return instance
        
        
class AccessLog(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_date = models.CharField(max_length=10, blank=True)
    created_month = models.CharField(max_length=7, blank=True)
    request_method = models.CharField(max_length=10)
    requested_uri = models.URLField(blank=True)
    query_string = models.CharField(max_length=500, blank=True)
    status_code = models.IntegerField(null=True)
    referer = models.URLField(blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ip_addr = models.GenericIPAddressField(null=True)
    latency = models.IntegerField(null=True)
    comment = models.TextField(blank=True)

    objects = AccessLogManager

    class Meta:
        db_table = 'account_access_logs'
        indexes = [
            models.Index(fields=['-created_month']),
            models.Index(fields=['-created_date']),
        ]
