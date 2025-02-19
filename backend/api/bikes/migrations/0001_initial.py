# Generated by Django 4.2.7 on 2024-03-18 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BikeStation",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.TextField()),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("capacity", models.IntegerField()),
            ],
            options={
                "db_table": "bike_stations",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="BikeDistance",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "distance",
                    models.FloatField(
                        help_text="Distance in meters between the two stations"
                    ),
                ),
                (
                    "station_from",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distances_from",
                        to="bikes.bikestation",
                    ),
                ),
                (
                    "station_to",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distances_to",
                        to="bikes.bikestation",
                    ),
                ),
            ],
            options={
                "db_table": "bike_distances",
                "managed": True,
            },
        ),
        migrations.CreateModel(
            name="BikeAvailability",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("harvest_time", models.DateTimeField()),
                ("last_update_time", models.DateTimeField()),
                ("available_bike_stands", models.IntegerField()),
                ("available_bikes", models.IntegerField()),
                ("status", models.TextField()),
                (
                    "station",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bikes.bikestation",
                    ),
                ),
            ],
            options={
                "db_table": "bike_availability",
                "managed": True,
            },
        ),
    ]
