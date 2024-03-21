# Generated by Django 5.0.3 on 2024-03-21 18:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=12)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loans.loan')),
            ],
        ),
    ]
