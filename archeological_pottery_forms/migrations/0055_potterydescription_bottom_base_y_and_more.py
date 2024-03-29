# Generated by Django 4.0.5 on 2022-11-02 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0054_remove_contourcorrelation_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='potterydescription',
            name='bottom_base_y',
            field=models.FloatField(blank=True, null=True, verbose_name='bottom_base_y'),
        ),
        migrations.AddField(
            model_name='potterydescription',
            name='lip_base_y',
            field=models.FloatField(blank=True, null=True, verbose_name='lip_base_y'),
        ),
        migrations.AddField(
            model_name='potterydescription',
            name='neck_base_y',
            field=models.FloatField(blank=True, null=True, verbose_name='neck_base_y'),
        ),
        migrations.AddField(
            model_name='potterydescription',
            name='shoulders_base_y',
            field=models.FloatField(blank=True, null=True, verbose_name='shoulders_base_y'),
        ),
    ]
