from django.utils import timezone
from rest_framework import viewsets


class BaseModelViewSet(viewsets.ModelViewSet):
    def perform_destroy(self, instance):
        instance.deleted = timezone.now()
        try:
            user = self.request.user
            if user.is_authenticated:
                instance.deleted_by = user.email
        except KeyError:
            pass
        instance.save()
