# Generated by Django 4.0.5 on 2022-12-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0070_contourcorrelation_correlation_avg'),
    ]

    operations = [
        migrations.AddField(
            model_name='contourgroup',
            name='correlation_avg',
            field=models.FloatField(default=0, verbose_name='correlation_avg'),
        ),
    ]
