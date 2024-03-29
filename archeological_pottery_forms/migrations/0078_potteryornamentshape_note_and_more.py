# Generated by Django 4.0.5 on 2022-12-19 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0077_potterydescription_width_avg'),
    ]

    operations = [
        migrations.AddField(
            model_name='potteryornamentshape',
            name='note',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='note'),
        ),
        migrations.AddField(
            model_name='potteryornamentshape',
            name='relative_ornament',
            field=models.IntegerField(null=True, verbose_name='relative_ornament'),
        ),
    ]
