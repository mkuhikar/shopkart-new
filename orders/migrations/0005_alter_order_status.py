# Generated by Django 3.2.5 on 2021-08-17 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20210810_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Accepted', 'Accepted')], default='New', max_length=10),
        ),
    ]
