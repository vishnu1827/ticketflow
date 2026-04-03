from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='🎭')
    color = models.CharField(max_length=20, default='#ff6b35')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    venue = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    date = models.DateTimeField()
    image_url = models.URLField(blank=True, default='')
    total_seats = models.PositiveIntegerField(default=100)
    booked_seats = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def available_seats(self):
        return self.total_seats - self.booked_seats

    @property
    def is_sold_out(self):
        return self.available_seats <= 0

    @property
    def occupancy_pct(self):
        if self.total_seats == 0:
            return 100
        return int((self.booked_seats / self.total_seats) * 100)

    class Meta:
        ordering = ['date']


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    booked_at = models.DateTimeField(auto_now_add=True)
    confirmation_code = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f"{self.user.username} — {self.event.title} ({self.confirmation_code})"

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            import string
            self.confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-booked_at']


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    card_last4 = models.CharField(max_length=4)
    card_holder = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=24, unique=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} — {self.status}"


class OTPVerification(models.Model):
    PURPOSE_CHOICES = [
        ('register', 'Registration'),
        ('login', 'Login'),
    ]
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='register')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp = str(random.randint(100000, 999999))
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.email} ({self.purpose})"

    class Meta:
        ordering = ['-created_at']
