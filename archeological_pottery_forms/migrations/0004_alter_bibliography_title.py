# Generated by Django 4.0.5 on 2022-06-29 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0003_alter_bibliography_report_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bibliography',
            name='title',
            field=models.CharField(help_text='enter the title of the report', max_length=500, verbose_name='Title'),
        ),
    ]