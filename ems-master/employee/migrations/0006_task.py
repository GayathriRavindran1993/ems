# Generated by Django 2.0 on 2020-11-20 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0005_auto_20180906_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_name', models.CharField(max_length=20)),
                ('task', models.CharField(max_length=20)),
                ('time', models.TimeField()),
            ],
        ),
    ]