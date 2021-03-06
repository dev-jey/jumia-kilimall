# Generated by Django 3.0.5 on 2020-10-07 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawlers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alldata',
            name='avg_rating',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='brand',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='discount',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='discount_percentage',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='image',
            field=models.CharField(max_length=2550),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='new_price',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='old_price',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alldata',
            name='total_ratings',
            field=models.CharField(max_length=255),
        ),
    ]
