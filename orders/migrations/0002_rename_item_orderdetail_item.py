# Generated by Django 3.2.5 on 2021-10-20 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderdetail',
            old_name='Item',
            new_name='item',
        ),
    ]