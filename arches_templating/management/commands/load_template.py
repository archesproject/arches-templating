import glob
import os
import uuid
import yaml
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files import File
from arches_templating.models import ArchesTemplate

class Command(BaseCommand):
    """
    Command for importing JSON-LD data into Arches
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-s", "--source", action="store", dest="source", help="the directory in which the data files are to be found"
        )

    def handle(self, *args, **options):
        source = options["source"]
        template_directory = os.path.dirname(source)
        template_id = None
        description = None
        template_name = None
        preview_file = None
        thumbnail_file = None
        saved_template_file = None
        saved_thumbnail_file = None
        saved_preview_file = None
        with open(source, 'rb') as source_file:
            config = yaml.safe_load(source_file)
        template_file_name = os.path.basename(config['file'])
        
        try:
            with open(os.path.join(template_directory, config['file']), 'rb') as template_file:
                saved_template_file = default_storage.save(template_file_name, File(template_file))
        except KeyError as e:
            raise Exception("Template file wasn't provided by yaml config", e)

        try:
            template_name = config['name']
        except KeyError:
            pass # ok, name is optional

        try:
            uuid_obj = uuid.UUID(config['id'])
            template_id = str(uuid_obj)
        except KeyError: # optional, but if not provided we will always create a new template
            uuid_obj = uuid.uuid4()
            template_id = str(uuid_obj)
        except ValueError:
            raise Exception("ID in config file must be a valid uuid", e)

        try:
            preview_file = glob.glob(os.path.join(template_directory, config['preview']))[0]
            with open(preview_file, 'rb') as source_file:
                saved_preview_file = default_storage.save(os.path.basename(preview_file), File(source_file))
        except (KeyError, FileNotFoundError):
            pass # preview file need not exist

        try:
            thumbnail_file = glob.glob(os.path.join(template_directory, config['thumbnail']))[0]
            
            with open(thumbnail_file, 'rb') as source_file:
                saved_thumbnail_file = default_storage.save(os.path.basename(thumbnail_file), File(source_file))
        except (KeyError, FileNotFoundError):
            pass # thumbnail file need not exist
        
        try:
            description = config['description']
        except KeyError:
            pass # description need not exist  
        
        if template_id:
            template, created = ArchesTemplate.objects.update_or_create(
                templateid=template_id,
                defaults={
                    'name':template_name,
                    'template':saved_template_file,
                    'description':description,
                    'preview':saved_preview_file,
                    'thumbnail':saved_thumbnail_file}
            )
        print(template)
        print(created)