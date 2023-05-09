import uuid
from django.db import models

class ArchesTemplate(models.Model):
    templateid = models.UUIDField(primary_key=True, unique=True)
    name = models.TextField(blank=False, null=False)
    template = models.FileField(upload_to="templates")
    description = models.TextField(blank=True, null=True)
    preview = models.FileField(upload_to="templates", null=True, blank=True)
    thumbnail = models.FileField(upload_to="templates", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        managed = True
        db_table = "arches_template"

    def __init__(self, *args, **kwargs):
        super(ArchesTemplate, self).__init__(*args, **kwargs)
        if not self.templateid:
            self.templateid = uuid.uuid4()