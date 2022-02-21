# Generated by Django 2.2.27 on 2022-02-21 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20220216_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='state',
            field=models.IntegerField(blank=True, choices=[(0, 'Needs review'), (1, 'Reviewed and published'), (2, 'Removed')], default=0, null=True),
        ),
    ]
