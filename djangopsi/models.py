from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class IndexedTimeStampedModel(models.Model):
    created = AutoCreatedField(_('created'), db_index=True)
    modified = AutoLastModifiedField(_('modified'), db_index=True)

    class Meta:
        abstract = True

class Environment(IndexedTimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    base_url = models.CharField(max_length=255)

    def __str__(self):
        return "{env.name} - {env.base_url}".format(env=self)

class Url(IndexedTimeStampedModel):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    environment = models.ForeignKey('Environment', related_name='urls', on_delete=models.CASCADE)

    def __str__(self):
        return "{url.name} - {url.path}".format(url=self)

class Report(IndexedTimeStampedModel):
    psi_id = models.CharField(max_length=255)
    strategy = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    score = models.FloatField()
    raw_data = JSONField()
    url = models.ForeignKey('Url', related_name='reports', on_delete=models.CASCADE)
    pass