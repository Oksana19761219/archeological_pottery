# Generated by Django 4.0.5 on 2022-07-04 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0013_alter_potterydescription_color_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bibliography',
            options={'ordering': ['research_year']},
        ),
        migrations.AlterModelOptions(
            name='potterydescription',
            options={'ordering': ['research_object_nr', 'find_registration_nr']},
        ),
    ]
