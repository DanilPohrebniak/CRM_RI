# Generated by Django 5.0 on 2024-01-15 16:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri', '0005_alter_documents_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods_in_stock',
            name='Unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ri.unit'),
        ),
    ]