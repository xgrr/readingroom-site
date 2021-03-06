# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-20 08:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailforms", "0003_capitalizeverbose"),
        ("wagtailcore", "0032_add_bulk_delete_page_permission"),
        ("wagtailredirects", "0005_capitalizeverbose"),
        ("home", "0025_auto_20170313_1053"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                ("organisation", models.CharField(blank=True, max_length=255)),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=255, verbose_name="Email Address"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Phone Number"
                    ),
                ),
                (
                    "preffered",
                    models.TextField(
                        blank=True, null=True, verbose_name="Prefered Form of Contact"
                    ),
                ),
                (
                    "message",
                    models.TextField(blank=True, null=True, verbose_name="Message"),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="MemberShipPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),
                ("telephone", models.CharField(blank=True, max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address_1", models.CharField(blank=True, max_length=255)),
                ("address_2", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=255)),
                ("country", models.CharField(blank=True, max_length=255)),
                ("post_code", models.CharField(blank=True, max_length=10)),
                ("intro", wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ("body", wagtail.wagtailcore.fields.RichTextField(blank=True)),
                (
                    "thank_you_text",
                    wagtail.wagtailcore.fields.RichTextField(blank=True),
                ),
                (
                    "to_address",
                    models.CharField(
                        blank=True,
                        help_text="Optional - form submissions will be emailed to this address",
                        max_length=255,
                    ),
                ),
                ("from_address", models.CharField(blank=True, max_length=255)),
                ("subject", models.CharField(blank=True, max_length=255)),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="MembershipRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=255, verbose_name="Email Address"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Phone Number"
                    ),
                ),
                ("message", models.TextField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="SpaceRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=255)),
                ("organisation", models.CharField(blank=True, max_length=255)),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=255, verbose_name="Email Address"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Phone Number"
                    ),
                ),
                (
                    "preffered",
                    models.TextField(
                        blank=True, null=True, verbose_name="Prefered Form of Contact"
                    ),
                ),
                (
                    "message",
                    models.TextField(
                        blank=True, null=True, verbose_name="Body of Inquiry"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.RenameModel(
            old_name="ContactPageCarouselItem", new_name="MemberShipPageCarouselItem"
        ),
        migrations.RemoveField(model_name="contactpage", name="feed_image"),
        migrations.RemoveField(model_name="contactpage", name="page_ptr"),
        migrations.AddField(
            model_name="bookspace",
            name="from_address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="bookspace",
            name="subject",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="bookspace",
            name="thank_you_text",
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name="bookspace",
            name="to_address",
            field=models.CharField(
                blank=True,
                help_text="Optional - form submissions will be emailed to this address",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="address_1",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="address_2",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="city",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="country",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="from_address",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="post_code",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="subject",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="telephone",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="thank_you_text",
            field=wagtail.wagtailcore.fields.RichTextField(blank=True),
        ),
        migrations.AddField(
            model_name="contactuspage",
            name="to_address",
            field=models.CharField(
                blank=True,
                help_text="Optional - form submissions will be emailed to this address",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="membershippagecarouselitem",
            name="page",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="carousel_items",
                to="home.MemberShipPage",
            ),
        ),
        migrations.DeleteModel(name="ContactPage"),
    ]
