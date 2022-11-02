# Generated by Django 4.0.5 on 2022-10-19 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archeological_pottery_forms', '0047_remove_potterydescription_distance_to_center'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='potterydescription',
            name='contour_group',
        ),
        migrations.AddField(
            model_name='contourgroup',
            name='correlation_x',
            field=models.FloatField(default=0.0, verbose_name='correlation_x'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='potterydescription',
            name='group',
            field=models.ManyToManyField(to='archeological_pottery_forms.contourgroup'),
        ),
    ]