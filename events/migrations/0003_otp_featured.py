from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0002_payment'),
    ]
    operations = [
        migrations.AddField(
            model_name='event',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(default='#ff6b35', max_length=20),
        ),
        migrations.CreateModel(
            name='OTPVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField()),
                ('otp', models.CharField(max_length=6)),
                ('purpose', models.CharField(choices=[('register','Registration'),('login','Login')], default='register', max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
