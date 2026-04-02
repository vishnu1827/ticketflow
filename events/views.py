from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q
from .models import Event, Booking, Category, Payment
import json, random, string


def home(request):
    events = Event.objects.filter(is_active=True, date__gte=timezone.now()).order_by('date')
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    city = request.GET.get('city', '')

    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(venue__icontains=query))
    if category_id:
        events = events.filter(category_id=category_id)
    if city:
        events = events.filter(city__icontains=city)

    cities = Event.objects.filter(is_active=True).values_list('city', flat=True).distinct()
    return render(request, 'events/home.html', {
        'events': events, 'categories': categories, 'cities': cities,
        'query': query, 'selected_category': category_id, 'selected_city': city,
    })


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    user_booked = False
    if request.user.is_authenticated:
        user_booked = Booking.objects.filter(user=request.user, event=event, status='confirmed').exists()
    return render(request, 'events/event_detail.html', {'event': event, 'user_booked': user_booked})


@login_required
def checkout(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    if event.is_sold_out:
        messages.error(request, 'Sorry, this event is sold out.')
        return redirect('event_detail', pk=pk)

    quantity = int(request.GET.get('qty', 1))
    quantity = max(1, min(10, quantity, event.available_seats))
    total = event.price * quantity

    return render(request, 'events/checkout.html', {
        'event': event,
        'quantity': quantity,
        'total': total,
    })


@login_required
def process_payment(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    if request.method != 'POST':
        return redirect('checkout', pk=pk)

    quantity = int(request.POST.get('quantity', 1))
    total = event.price * quantity
    card_number = request.POST.get('card_number', '').replace(' ', '')
    card_holder = request.POST.get('card_holder', '').strip()
    expiry = request.POST.get('expiry', '')
    cvv = request.POST.get('cvv', '')

    # Simulate: card ending in 0000 = decline
    last4 = card_number[-4:] if len(card_number) >= 4 else '0000'
    if last4 == '0000':
        messages.error(request, '❌ Payment declined. Please try a different card.')
        return redirect('checkout', pk=pk)

    # Create booking
    booking = Booking.objects.create(
        user=request.user, event=event,
        quantity=quantity, total_price=total,
        status='confirmed',
    )
    event.booked_seats += quantity
    event.save()

    # Create payment record
    txn_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    Payment.objects.create(
        booking=booking,
        card_last4=last4,
        card_holder=card_holder,
        amount=total,
        status='success',
        transaction_id=txn_id,
    )

    # Email confirmation
    send_mail(
        subject=f'🎟 Booking Confirmed — {event.title}',
        message=(
            f'Hi {request.user.first_name or request.user.username},\n\n'
            f'Your booking is confirmed!\n\n'
            f'Event: {event.title}\n'
            f'Date: {event.date.strftime("%d %b %Y, %I:%M %p")}\n'
            f'Venue: {event.venue}, {event.city}\n'
            f'Tickets: {quantity}\n'
            f'Total Paid: ₹{total}\n'
            f'Transaction ID: {txn_id}\n'
            f'Confirmation Code: {booking.confirmation_code}\n\n'
            f'See you there! 🎉\nTicketFlow Team'
        ),
        from_email=None,
        recipient_list=[request.user.email],
        fail_silently=True,
    )

    return redirect('payment_success', pk=booking.pk)


@login_required
def payment_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'events/payment_success.html', {'booking': booking})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('event', 'payment')
    return render(request, 'events/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user, status='confirmed')
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        booking.event.booked_seats = max(0, booking.event.booked_seats - booking.quantity)
        booking.event.save()
        messages.success(request, 'Booking cancelled successfully.')
    return redirect('my_bookings')


def calendar_view(request):
    events = Event.objects.filter(is_active=True, date__gte=timezone.now()).order_by('date')
    events_json = json.dumps([{
        'id': e.pk, 'title': e.title,
        'start': e.date.strftime('%Y-%m-%dT%H:%M:%S'),
        'url': f'/event/{e.pk}/',
        'color': '#ff6b35' if e.is_sold_out else '#00d4aa',
        'extendedProps': {'venue': e.venue, 'city': e.city, 'price': str(e.price), 'available': e.available_seats}
    } for e in events])
    return render(request, 'events/calendar.html', {'events_json': events_json})


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to TicketFlow, {user.username}! 🎟')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})
