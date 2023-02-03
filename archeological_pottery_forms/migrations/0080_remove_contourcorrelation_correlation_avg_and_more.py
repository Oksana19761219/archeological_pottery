# Generated by Django 4.0.5 on 2023-02-02 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0079_ceramiccontour_curvature'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contourcorrelation',
            name='correlation_avg',
        ),
        migrations.RemoveField(
            model_name='contourcorrelation',
            name='correlation_x_body',
        ),
        migrations.RemoveField(
            model_name='contourcorrelation',
            name='correlation_x_neck',
        ),
        migrations.RemoveField(
            model_name='contourcorrelation',
            name='correlation_x_shoulders',
        ),
        migrations.AddField(
            model_name='contourcorrelation',
            name='correlation_curvature',
            field=models.FloatField(blank=True, null=True, verbose_name='correlation_curvature'),
        ),
    ]