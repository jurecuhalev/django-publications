# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import publications.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("description", models.CharField(max_length=256)),
                ("file", models.FileField(upload_to=b"publications/")),
            ],
        ),
        migrations.CreateModel(
            name="CustomLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("description", models.CharField(max_length=256)),
                ("url", models.URLField(verbose_name=b"URL")),
            ],
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "citekey",
                    models.CharField(
                        help_text=b"BibTex citation key. Leave blank if unsure.",
                        max_length=512,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=512, verbose_name="Publication Title"),
                ),
                (
                    "authors",
                    models.CharField(
                        help_text=b"List of authors separated by commas or <i>and</i>.",
                        max_length=2048,
                    ),
                ),
                (
                    "year",
                    models.PositiveIntegerField(
                        max_length=4,
                        verbose_name="Year of Publication",
                        choices=[
                            (2005, 2005),
                            (2006, 2006),
                            (2007, 2007),
                            (2008, 2008),
                            (2009, 2009),
                            (2010, 2010),
                            (2011, 2011),
                            (2012, 2012),
                            (2013, 2013),
                            (2014, 2014),
                            (2015, 2015),
                            (2016, 2016),
                            (2017, 2017),
                            (2018, 2018),
                            (2019, 2019),
                            (2020, 2020),
                            (2021, 2021),
                            (2022, 2022),
                            (2023, 2023),
                        ],
                    ),
                ),
                (
                    "month",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Month of Publication",
                        choices=[
                            (1, b"January"),
                            (2, b"February"),
                            (3, b"March"),
                            (4, b"April"),
                            (5, b"May"),
                            (6, b"June"),
                            (7, b"July"),
                            (8, b"August"),
                            (9, b"September"),
                            (10, b"October"),
                            (11, b"November"),
                            (12, b"December"),
                        ],
                    ),
                ),
                ("journal", models.CharField(max_length=256, blank=True)),
                ("book_title", models.TextField(blank=True)),
                ("publisher", models.CharField(max_length=256, blank=True)),
                ("institution", models.CharField(max_length=256, blank=True)),
                ("pages", publications.fields.PagesField(max_length=32, blank=True)),
                ("note", models.TextField(blank=True)),
                (
                    "keywords",
                    models.TextField(
                        help_text=b"List of keywords separated by commas.", blank=True
                    ),
                ),
                (
                    "url",
                    models.TextField(
                        help_text=b"Link to PDF or journal page.",
                        verbose_name=b"URL",
                        blank=True,
                    ),
                ),
                (
                    "code",
                    models.URLField(help_text=b"Link to page with code.", blank=True),
                ),
                (
                    "pdf",
                    models.FileField(
                        upload_to=b"publications/",
                        null=True,
                        verbose_name=b"PDF",
                        blank=True,
                    ),
                ),
                (
                    "doi",
                    models.CharField(max_length=128, verbose_name=b"DOI", blank=True),
                ),
                (
                    "external",
                    models.BooleanField(
                        help_text=b"If publication was written in another lab, mark as external."
                    ),
                ),
                ("abstract", models.TextField(blank=True)),
                (
                    "isbn",
                    models.CharField(
                        help_text=b"Only for a book.",
                        max_length=32,
                        verbose_name=b"ISBN",
                        blank=True,
                    ),
                ),
                ("timestamp", models.DateField(auto_now_add=True)),
                (
                    "owner",
                    models.CharField(
                        default=b"admin", max_length=64, null=True, blank=True
                    ),
                ),
                ("language", models.CharField(max_length=255, blank=True)),
                ("editor", models.CharField(max_length=255, blank=True)),
                (
                    "address",
                    models.CharField(
                        max_length=255, verbose_name="Published address", blank=True
                    ),
                ),
                ("organization", models.CharField(max_length=255, blank=True)),
                ("volume", models.CharField(max_length=255, blank=True)),
                ("number", models.CharField(max_length=255, blank=True)),
                ("series", models.CharField(max_length=255, blank=True)),
                ("edition", models.CharField(max_length=255, blank=True)),
                ("chapter", models.CharField(max_length=255, blank=True)),
                ("school", models.CharField(max_length=255, blank=True)),
                (
                    "howpublished",
                    models.CharField(
                        max_length=255, verbose_name="How is it published?", blank=True
                    ),
                ),
                ("issn", models.CharField(max_length=255, blank=True)),
                ("comment", models.TextField(blank=True)),
                (
                    "state",
                    models.IntegerField(
                        default=0,
                        max_length=5,
                        null=True,
                        blank=True,
                        choices=[
                            (0, b"Needs review"),
                            (1, b"Reviewed and published"),
                            (2, b"Removed"),
                        ],
                    ),
                ),
                (
                    "owner_user",
                    models.ForeignKey(
                        related_name="publication_owner_user",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ["-year", "-month", "-id"],
                "verbose_name_plural": " Publications",
            },
        ),
        migrations.CreateModel(
            name="Type",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("order", models.PositiveIntegerField(editable=False)),
                ("type", models.CharField(max_length=128)),
                ("description", models.CharField(max_length=128)),
                (
                    "bibtex_types",
                    models.TextField(
                        default=b"article",
                        help_text=b"Possible BibTex types, separated by comma.",
                        verbose_name=b"BibTex types",
                    ),
                ),
                (
                    "hidden",
                    models.BooleanField(help_text=b"Hide publications from main view."),
                ),
            ],
            options={
                "ordering": ("order",),
            },
        ),
        migrations.AddField(
            model_name="publication",
            name="type",
            field=models.ForeignKey(to="publications.Type"),
        ),
        migrations.AddField(
            model_name="publication",
            name="user",
            field=models.ForeignKey(
                related_name="publication_user",
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="customlink",
            name="publication",
            field=models.ForeignKey(to="publications.Publication"),
        ),
        migrations.AddField(
            model_name="customfile",
            name="publication",
            field=models.ForeignKey(to="publications.Publication"),
        ),
    ]
