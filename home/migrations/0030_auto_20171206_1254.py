# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-06 12:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("home", "0029_auto_20171206_1016")]

    operations = [
        migrations.AlterField(
            model_name="formfield",
            name="field_type",
            field=models.CharField(
                choices=[
                    ("singleline", "Single line text"),
                    ("multiline", "Multi-line text"),
                    ("email", "Email"),
                    ("number", "Number"),
                    ("url", "URL"),
                    ("checkbox", "Checkbox"),
                    ("checkboxes", "Checkboxes"),
                    ("dropdown", "Drop down"),
                    ("radio", "Radio buttons"),
                    ("date", "Date"),
                    ("datetime", "Date/time"),
                ],
                max_length=16,
                verbose_name="field type",
            ),
        )
    ]
