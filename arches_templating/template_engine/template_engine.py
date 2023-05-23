import base64
import copy
import re
from typing import List, Tuple
from arches_templating.template_engine.template_tag import TemplateTag
from arches_templating.template_engine.template_tag_type import TemplateTagType
import requests

class TemplateEngine(object):
    def __init__(
        self,
        regex=None,
    ):
        self.regex = re.compile(regex if regex else r"(<arches:(\w+)([\S\s]*?)>)")

    def extract_tags(self, template) -> List[TemplateTag]:
        tags = []
        tag_matches = self.extract_regex_matches(template)
        context: List[TemplateTag] = []
        tag_type = None

        for match in tag_matches:
            tag_match = match[0]
            attributes = {}

            try:
                optional_keys = match[1]
            except IndexError:
                optional_keys = None

            raw = tag_match[0]
            if tag_match[1] == "value":
                tag_type = TemplateTagType.VALUE
            if tag_match[1] == "image":
                tag_type = TemplateTagType.IMAGE
            elif tag_match[1] == "context":
                tag_type = TemplateTagType.CONTEXT
            elif tag_match[1] == "if":
                tag_type = TemplateTagType.IF
            elif tag_match[1] == "end":
                tag_type = TemplateTagType.END

            if len(tag_match) > 2:
                raw_attributes = tag_match[2].split()
                for attribute in raw_attributes:
                    split_attribute = attribute.split("=")
                    if len(split_attribute) == 2:
                        attributes[split_attribute[0]] = split_attribute[1].strip("\"'“”")
                if tag_type == None:
                    raise ("Unsupported Tag - cannot proceed:" + tag_match[0])

            if tag_type == TemplateTagType.CONTEXT or tag_type == TemplateTagType.IF:
                context_tag = TemplateTag(raw, tag_type, attributes, optional_keys)
                if len(context) == 0:
                    tags.append(context_tag)
                else:
                    context[-1].children.append(context_tag)
                context.append(context_tag)
            elif tag_type == TemplateTagType.END:
                context[-1].end_tag = TemplateTag(raw, tag_type, attributes, optional_keys)
                context.pop()
            elif len(context) == 0:
                tags.append(TemplateTag(raw, tag_type, attributes, optional_keys))
            else:
                context[-1].children.append(TemplateTag(raw, tag_type, attributes, optional_keys))
        return tags

    # the subclass needs to implement this method to hand back a tuple of unprocessed tag information
    def extract_regex_matches(self, template, regex) -> List[Tuple]:
        pass

    def normalize_dictionary_keys(self, dictionary):
        new_dictionary = {}
        for key, value in dictionary.items():
            # Normalize the key by removing leading/trailing whitespace and converting to lowercase
            norm_key = key.strip().replace(" ", "_").lower()
            # Store the value in the dictionary with the normalized key
            new_dictionary[norm_key] = value

        return {**dictionary, **new_dictionary}

    def traverse_dictionary(self, path, dictionary):
        path_parts = path.split("/")
        current_value = dictionary

        for part in path_parts:
            if isinstance(current_value, dict):
                current_value = self.normalize_dictionary_keys(current_value)
                current_value = current_value.get(part, None)
            elif isinstance(current_value, List) and part.isnumeric():
                try:
                    current_value = current_value[int(part)]
                except IndexError:
                    current_value = None  # this is ok, allows us to continue writing to the template.
        return current_value

    def get_tag_values(self, tags, context) -> List[TemplateTag]:
        extended_tags = []

        for tag in tags:
            if tag.type == TemplateTagType.VALUE:
                path_value = tag.attributes.get("path", None)
                if path_value is not None:
                    tag.value = self.traverse_dictionary(path_value, context)
                else:
                    tag.value = ""
            if tag.type == TemplateTagType.IMAGE:
                path_value = tag.attributes.get("path", None)
                if path_value:
                    image_value = self.traverse_dictionary(path_value, context)
                    if re.match("^http", image_value):
                        tag.value = "data:image/jpeg;base64," + base64.b64encode(requests.get(image_value).content).decode('utf-8')
                    else:
                        tag.value = image_value
                extended_tags.append(tag)
            elif tag.type == TemplateTagType.CONTEXT:
                path_value = tag.attributes.get("path", None)
                index_value = tag.attributes.get("index", None)
                if path_value:
                    new_context = self.traverse_dictionary(path_value, context)
                    if isinstance(new_context, List) and index_value:
                        self.get_tag_values(tag.children, new_context[int(index_value)])
                    elif isinstance(new_context, List):
                        tag.has_rows = True
                        tag.context_children_template = tag.children
                        tag.children = []
                        for item in new_context:
                            tag.children.extend(self.get_tag_values(copy.deepcopy(tag.context_children_template), item))
                            tag.children.append(TemplateTag("", TemplateTagType.ROWEND))
                    else:
                        self.get_tag_values(tag.children, new_context)
            elif tag.type == TemplateTagType.IF:
                path_value = tag.attributes.get("path", None)
                inverse_value:str = tag.attributes.get("inverse", "")
                inverse = True if inverse_value.lower() == "true" else False
                if path_value:
                    tag_value = self.traverse_dictionary(path_value, context)
                else:
                    tag_value = False
                
                tag.render = tag_value if inverse is False else not tag_value
                
                if tag.render:
                    self.get_tag_values(tag.children, context) # use the existing context; if tags do not generate a new context.
                
            elif tag.type == TemplateTagType.END:
                context.pop()

        return tags

    def create_file(self, tags, template):
        pass

    # Primary entrypoint; pass in a template to be formatted and the root resource with which to do it.
    def document_replace(self, template, context):
        tags = self.extract_tags(template)

        expanded_tags = self.get_tag_values(tags, context)
        return self.create_file(expanded_tags, template)
