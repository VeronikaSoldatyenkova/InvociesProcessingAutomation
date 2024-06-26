# Generated by Django 5.0.6 on 2024-05-28 12:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("automation_app", "0002_automationlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutomationType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("order_processing", "Order Processing"),
                    ("invoice_processing", "Invoice Processing"),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="automation",
            name="automation_type",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="automation_app.automationtype",
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="UserAutomation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="automation_app.automation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
