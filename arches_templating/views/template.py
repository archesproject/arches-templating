
import os
import logging
import json
from io import BytesIO, StringIO

from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.views import generic

from arches.app.utils.response import JSONResponse

from arches_templating.models import ArchesTemplate
from arches_templating.template_engine.template_engine_factory import TemplateEngineFactory


class TemplateView(generic.View):

    logger = logging.getLogger(__name__)

    def get(request):
        arches_templates = ArchesTemplate.objects.all()
        return JSONResponse(arches_templates.values())

    def post(self, request, templateid):
        json_data = json.loads(request.body)
        #template_id = json_data["templateId"] if "templateId" in json_data else None
        template_record = ArchesTemplate.objects.get(pk=templateid)
        template = template_record.template.name
        #template = settings.AFS_CUSTOM_REPORTS[template_id] if template_id in settings.AFS_CUSTOM_REPORTS else None


        bytestream = BytesIO()
        extension = os.path.splitext(template)[1].replace(".", "")
        factory = TemplateEngineFactory()
        engine = factory.create_engine(extension)
        with template_record.template.open('rb') as f:
            source_stream = BytesIO(f.read())
        (bytestream, mime, title) = engine.document_replace(source_stream, json_data)

        bytestream.seek(0)

        if template is None:
            return HttpResponseServerError("Could not find requested template")

        response = HttpResponse(content=bytestream.read())
        response["Content-Type"] = mime
        response["Content-Disposition"] = "attachment; filename={}".format(title)
        return response