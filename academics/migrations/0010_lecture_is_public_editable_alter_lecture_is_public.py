# Generated by Django 4.2.19 on 2025-03-12 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0009_alter_syllabus_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='is_public_editable',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='is_public',
            field=models.BooleanField(default=True, editable=False),
        ),
    ]
