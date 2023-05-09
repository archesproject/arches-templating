from arches_templating.views.index import IndexView
from arches_templating.views.template import TemplateView
from django.urls import path, re_path

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('template/<uuid:templateid>', TemplateView.as_view(), name="archestemplating_template_view"),
    re_path(r'template\/?', TemplateView.get, name="archestemplating_template_view_get"),
]