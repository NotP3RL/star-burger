# Generated by Django 3.2.15 on 2024-04-09 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_order_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='price',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(db_index=True, decimal_places=2, default=3, max_digits=8, verbose_name='цена'),
            preserve_default=False,
        ),
    ]
