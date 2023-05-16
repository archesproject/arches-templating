
from enum import Enum

class TemplateTagType(Enum):
    VALUE = 1
    CONTEXT = 2
    END = 3
    ROWEND = 4
    IMAGE = 5
    IF = 6