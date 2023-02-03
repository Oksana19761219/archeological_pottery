# Generated by Django 4.0.5 on 2022-12-15 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0072_remove_contourgroup_correlation_avg'),
    ]

    operations = [
        migrations.AddField(
            model_name='potterydescription',
            name='neck_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='neck_type'),
        ),
        migrations.AddField(
            model_name='potterydescription',
            name='shoulders_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='shoulders_type'),
        ),
    ]