from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[('pending_payment','Pending Payment'),('confirmed','Confirmed'),('cancelled','Cancelled')],
                default='pending_payment', max_length=20),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_last4', models.CharField(max_length=4)),
                ('card_holder', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending','Pending'),('success','Success'),('failed','Failed')], default='pending', max_length=10)),
                ('transaction_id', models.CharField(max_length=24, unique=True)),
                ('paid_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='events.booking')),
            ],
        ),
    ]
