# Generated by Django 4.0.5 on 2022-10-20 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0053_contourcorrelation_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contourcorrelation',
            name='group',
        ),
    ]
