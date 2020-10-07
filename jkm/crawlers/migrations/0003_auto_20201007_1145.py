# Generated by Django 3.0.5 on 2020-10-07 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlers', '0002_auto_20201007_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alldata',
            name='avg_rating',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='brand',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='discount',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='discount_percentage',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='image',
            field=models.CharField(blank=True, max_length=2550, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='link',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='new_price',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='old_price',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='total_ratings',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
