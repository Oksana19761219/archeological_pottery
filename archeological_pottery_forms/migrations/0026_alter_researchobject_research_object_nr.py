# Generated by Django 4.0.5 on 2022-07-11 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0025_alter_potterymakingaction_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researchobject',
            name='research_object_nr',
            field=models.IntegerField(help_text='temporary field, object id from old database', null=True, verbose_name='research object number'),
        ),
    ]
