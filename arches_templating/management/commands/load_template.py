import glob
import os
import uuid
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
        template_file_name = os.path.basename(source)
        template_directory = os.path.dirname(source)
        template_id = None
        description = None
        template_prefix = None
        template_suffix = None
        template_name = None
        preview_file = None
        thumbnail_file = None
        saved_template_file = None
        saved_thumbnail_file = None
        saved_preview_file = None
        template_name_split = template_file_name.split('_')
        try:
            template_prefix = template_name_split[0]
            with open(source, 'rb') as source_file:
                saved_template_file = default_storage.save(template_file_name, File(source_file))

        except IndexError:
            raise Exception("Template name formatted incorrectly.  Must be in the form of uuid_template_[name].ext - where name is optional.")

        try:
            template_suffix = template_name_split[2]
            template_suffix = template_suffix.split('.')[0]
            template_name = template_suffix.replace('-', ' ')
        except IndexError:
            pass # ok, name is optional

        try:
            uuid_obj = uuid.UUID(template_prefix)
            template_id = str(uuid_obj)
        except ValueError:
            pass

        try:
            print(os.path.join(template_directory, template_id + "_preview.*"))
            preview_file = glob.glob(os.path.join(template_directory, "{}_preview.*".format(template_id)))[0]
            with open(preview_file, 'rb') as source_file:
                saved_preview_file = default_storage.save(os.path.basename(preview_file), File(source_file))
        except (IndexError, FileNotFoundError):
            pass # preview file need not exist

        try:
            thumbnail_file = glob.glob(os.path.join(template_directory, "{}_thumbnail.*".format(template_id)))[0]
            
            with open(thumbnail_file, 'rb') as source_file:
                saved_thumbnail_file = default_storage.save(os.path.basename(thumbnail_file), File(source_file))
        except (IndexError, FileNotFoundError):
            pass # preview file need not exist
        
        try:
            with open(os.path.join(template_directory, "{}_description.txt".format(template_id)), 'r') as description_file:
                description = description_file.read()
        except FileNotFoundError:
            pass # description file need not exist  
        
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