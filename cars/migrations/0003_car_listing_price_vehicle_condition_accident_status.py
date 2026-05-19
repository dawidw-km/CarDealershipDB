from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0002_car_moderation_status_car_owner_car_reviewer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='car',
            old_name='purchase_price',
            new_name='listing_price',
        ),
        migrations.RemoveField(
            model_name='car',
            name='selling_price',
        ),
        migrations.AddField(
            model_name='car',
            name='vehicle_condition',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('used', 'Used'),
                    ('for_parts', 'For parts'),
                ],
                default='used',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='car',
            name='accident_status',
            field=models.CharField(
                choices=[
                    ('accident_free', 'Accident free'),
                    ('after_impact', 'After impact'),
                    ('accident_history', 'Accident history'),
                    ('damaged', 'Damaged'),
                ],
                default='accident_free',
                max_length=20,
            ),
        ),
    ]
