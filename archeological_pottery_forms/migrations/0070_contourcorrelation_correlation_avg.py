# Generated by Django 4.0.5 on 2022-12-14 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0069_contourgroup_length_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='contourcorrelation',
            name='correlation_avg',
            field=models.FloatField(blank=True, null=True, verbose_name='correlation_avg'),
        ),
    ]