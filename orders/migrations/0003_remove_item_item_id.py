# Generated by Django 3.2.5 on 2021-10-20 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_rename_item_orderdetail_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='item_id',
        ),
    ]