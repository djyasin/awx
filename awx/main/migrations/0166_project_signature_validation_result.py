# Generated by Django 3.2.13 on 2022-07-26 19:52

import awx.main.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0165_added_contentsigning_to_project_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='signature_validation_result',
            field=awx.main.fields.JSONBlob(blank=True, default=None, editable=False, null=True),
        ),
    ]
