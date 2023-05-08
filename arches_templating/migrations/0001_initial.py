# Generated by Django 3.2.18 on 2023-05-03 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArchesTemplate',
            fields=[
                ('templateid', models.UUIDField(primary_key=True, serialize=False, unique=True)),
                ('name', models.TextField()),
                ('template', models.FileField(upload_to='templates')),
                ('description', models.TextField(blank=True, null=True)),
                ('preview', models.FileField(upload_to='templates', null=True, blank=True)),
                ('thumbnail', models.FileField(upload_to='templates', null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'arches_template',
                'managed': True,
            },
        ),
    ]
