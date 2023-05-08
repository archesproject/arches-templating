from logging import Logger
import logging
from typing import Callable
from arches_templating.template_engine.template_engine import TemplateEngine

logger = logging.getLogger(__name__)

class TemplateEngineFactory(object):
    registry = {}

    @classmethod
    def register(cls, name:str):
        def inner_wrapper(wrapped_class: TemplateEngine) -> Callable:
            if name in cls.registry:
                logger.warning('Template Engine %s already exists. Will replace it', name)
            cls.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    @classmethod
    def create_engine(cls, name: str, **kwargs) -> 'TemplateEngine':
        """ Factory command to create the template engine """

        template_engine_class = cls.registry[name]
        template_engine = template_engine_class(**kwargs)
        return template_engine