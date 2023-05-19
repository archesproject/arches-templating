
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
from django.views.decorators.csrf import csrf_exempt

class TemplateView(generic.View):

    logger = logging.getLogger(__name__)

    def get(request):
        all_templates = ArchesTemplate.objects.all()
        response = []
        for template in all_templates:
            template_object = {}
            template_object['templateid'] = template.templateid
            template_object['name'] = template.name
            template_object['description'] = template.description
            template_object['template'] = {}
            template_object['template']['url'] = template.template.url
            template_object['template']['name'] = template.template.name
            if template.preview:
                template_object['preview'] = {}
                template_object['preview']['url'] = template.preview.url
                template_object['preview']['name'] = template.preview.url
            if template.thumbnail:
                template_object['thumbnail'] = {}
                template_object['thumbnail']['url'] = template.thumbnail.url
                template_object['thumbnail']['name'] = template.thumbnail.name
            response.append(template_object)
        return JSONResponse(response)
    
    @csrf_exempt
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