# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-11 10:51
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [("home", "0032_auto_20171211_0819")]

    operations = [
        migrations.RenameField(
            model_name="blogpage", old_name="tease", new_name="tease_en"
        ),
        migrations.AddField(
            model_name="blogpage",
            name="tease_pt",
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name="blogpage",
            name="tease_tet",
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
    ]
