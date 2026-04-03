from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/<int:pk>/checkout/', views.checkout, name='checkout'),
    path('event/<int:pk>/pay/', views.process_payment, name='process_payment'),
    path('booking/<int:pk>/success/', views.payment_success, name='payment_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login_otp'),
]
