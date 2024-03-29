# Generated by Django 5.0 on 2024-01-15 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ri', '0003_doctype_remove_documents_income_documents_doctype'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='counterparty',
            options={'verbose_name_plural': 'Counterparties'},
        ),
        migrations.AlterModelOptions(
            name='documents',
            options={'verbose_name_plural': 'Documents'},
        ),
        migrations.AlterModelOptions(
            name='sales',
            options={'verbose_name_plural': 'Sales'},
        ),
        migrations.AddField(
            model_name='goods_in_stock',
            name='Sum',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
