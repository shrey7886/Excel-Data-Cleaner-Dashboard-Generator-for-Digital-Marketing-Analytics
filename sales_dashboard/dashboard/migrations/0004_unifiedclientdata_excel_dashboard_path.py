# Generated by Django 5.2.4 on 2025-07-06 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_unifiedclientdata_clientprediction'),
    ]

    operations = [
        migrations.AddField(
            model_name='unifiedclientdata',
            name='excel_dashboard_path',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
