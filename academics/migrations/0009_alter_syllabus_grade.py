# Generated by Django 4.2.19 on 2025-03-12 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0008_alter_syllabus_grade_alter_syllabus_instructor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='syllabus',
            name='grade',
            field=models.CharField(blank=True, verbose_name='対象学年'),
        ),
    ]
