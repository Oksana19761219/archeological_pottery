# Generated by Django 4.0.5 on 2022-12-16 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0074_potterydescription_neck_slope_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='potterylipshape',
            name='relative_lip',
            field=models.IntegerField(null=True, verbose_name='relative_lip'),
        ),
    ]
