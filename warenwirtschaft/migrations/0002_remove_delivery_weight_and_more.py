# Generated by Django 5.1.4 on 2025-04-06 06:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warenwirtschaft', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='warenwirtschaft.supplier'),
        ),
        migrations.AlterField(
            model_name='deliveryunit',
            name='delivery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveryunits', to='warenwirtschaft.delivery'),
        ),
        migrations.AlterField(
            model_name='deliveryunit',
            name='material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='material', to='warenwirtschaft.material'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='note',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Anmerkung'),
        ),
        migrations.AlterField(
            model_name='unload',
            name='delivery_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unload_delivery_unit', to='warenwirtschaft.deliveryunit'),
        ),
        migrations.AlterField(
            model_name='unload',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unload_supplier', to='warenwirtschaft.supplier'),
        ),
    ]
