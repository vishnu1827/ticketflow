from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('icon', models.CharField(default='🎭', max_length=50)),
            ],
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('venue', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('date', models.DateTimeField()),
                ('image_url', models.URLField(blank=True, default='')),
                ('total_seats', models.PositiveIntegerField(default=100)),
                ('booked_seats', models.PositiveIntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.category')),
            ],
            options={'ordering': ['date']},
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='confirmed', max_length=20)),
                ('booked_at', models.DateTimeField(auto_now_add=True)),
                ('confirmation_code', models.CharField(max_length=12, unique=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='auth.user')),
            ],
            options={'ordering': ['-booked_at']},
        ),
    ]
