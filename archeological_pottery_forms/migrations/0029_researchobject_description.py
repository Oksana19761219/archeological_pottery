# Generated by Django 4.0.5 on 2022-07-12 17:05

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0028_alter_potterydescription_arc_length_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchobject',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True, verbose_name='description'),
        ),
    ]
