from arches_templating.views.index import IndexView
from arches_templating.views.template import TemplateView
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path(
        "template/<uuid:templateid>",
        csrf_exempt(TemplateView.as_view()),
        name="archestemplating_template_view",
    ),
    re_path(r"template\/?", TemplateView.get, name="archestemplating_template_view_get"),
]
