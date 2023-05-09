from django.contrib import admin
from arches_templating import models

admin.site.register(
    [
        models.ArchesTemplate
    ]
)