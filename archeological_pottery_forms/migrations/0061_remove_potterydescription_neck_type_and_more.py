# Generated by Django 4.0.5 on 2022-11-09 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0060_potterydescription_neck_shoulders_union_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potterydescription',
            name='neck_type',
        ),
        migrations.RemoveField(
            model_name='potterydescription',
            name='shoulders_type',
        ),
    ]
