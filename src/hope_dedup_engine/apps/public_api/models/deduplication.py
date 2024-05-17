from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope_dedup_engine.apps.security.models import ExternalSystem


class DeduplicationSet(models.Model):
    class Status(models.IntegerChoices):
        CLEAN = 0, _("Clean")  # Deduplication set is created or already processed
        DIRTY = 1, _("Dirty")  # Images are added to deduplication set, but not yet processed
        PROCESSING = 2, _("Processing")  # Images are being processed

    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    reference_pk = models.IntegerField()
    state = models.IntegerField(
        choices=Status.choices,
        default=Status.CLEAN,
    )
    deleted = models.BooleanField(_("deleted"), null=False, blank=False, default=False)
    external_system = models.ForeignKey(ExternalSystem, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    deduplication_set = models.ForeignKey(DeduplicationSet, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        unique_together = ("deduplication_set", "filename")
