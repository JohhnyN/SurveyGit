# Generated by Django 4.1.5 on 2023-02-01 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djf', '0002_alter_answer_options_alter_question_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='description',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Описание'),
        ),
    ]
