# Generated by Django 4.0.5 on 2022-07-16 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0029_researchobject_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='potterydescription',
            name='drawing',
            field=models.ImageField(null=True, upload_to='drawings', verbose_name='drawing'),
        ),
    ]
