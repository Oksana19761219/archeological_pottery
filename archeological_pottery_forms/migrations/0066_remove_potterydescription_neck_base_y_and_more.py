# Generated by Django 4.0.5 on 2022-12-05 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0065_remove_potterydescription_bottom_y'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potterydescription',
            name='neck_base_y',
        ),
        migrations.RemoveField(
            model_name='potterydescription',
            name='shoulders_base_y',
        ),
    ]
