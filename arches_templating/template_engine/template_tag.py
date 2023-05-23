

from ast import List

from arches_templating.template_engine.template_tag_type import TemplateTagType

class TemplateTag(object):
    def __init__(self, raw: str, tag_type: TemplateTagType, attributes: dict = {}, optional_keys: dict = {}):
        self.type = tag_type
        self.attributes = attributes  # context is relative to the r
        self.raw = raw
        self.value = None
        self.children: List[TemplateTag] = []
        self.end_tag = None
        self.optional_keys = optional_keys
        self.has_rows = False
        self.context_children_template = None
        self.render = True