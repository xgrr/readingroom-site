# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-04-20 14:43
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [("home", "0045_auto_20180418_0643")]

    operations = [
        migrations.AddField(
            model_name="blogindexpage",
            name="title_en",
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name="blogindexpage",
            name="title_tet",
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
    ]