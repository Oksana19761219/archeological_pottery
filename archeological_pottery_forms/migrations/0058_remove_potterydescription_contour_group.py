# Generated by Django 4.0.5 on 2022-11-04 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0057_remove_potterydescription_bottom_base_y_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potterydescription',
            name='contour_group',
        ),
    ]
