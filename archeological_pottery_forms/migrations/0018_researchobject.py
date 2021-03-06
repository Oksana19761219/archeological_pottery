# Generated by Django 4.0.5 on 2022-07-06 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0017_alter_bibliographicreference_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('research_object_nr', models.IntegerField(help_text='enter research object number', null=True, verbose_name='research object number')),
                ('name', models.CharField(help_text='name of research object, object description', max_length=500, verbose_name='title')),
                ('year', models.CharField(help_text='enter the year of archaeological research', max_length=50, verbose_name='year')),
                ('research_type', models.CharField(max_length=250, verbose_name='research type')),
            ],
            options={
                'verbose_name': 'research object',
                'verbose_name_plural': 'research objects',
                'ordering': ['year', 'research_type'],
            },
        ),
    ]
