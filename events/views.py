from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from .models import Event, Booking, Category, Payment, OTPVerification
import json, random, string


# ── HOME ──────────────────────────────────────────────────────────────────────
def home(request):
    events = Event.objects.filter(is_active=True, date__gte=timezone.now()).order_by('date')
    featured = events.filter(is_featured=True)[:3]
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    city = request.GET.get('city', '')

    if query:
        events = events.filter(Q(title__icontains=query)|Q(description__icontains=query)|Q(venue__icontains=query))
    if category_id:
        events = events.filter(category_id=category_id)
    if city:
        events = events.filter(city__icontains=city)

    cities = Event.objects.filter(is_active=True).values_list('city', flat=True).distinct()
    return render(request, 'events/home.html', {
        'events': events, 'featured': featured,
        'categories': categories, 'cities': cities,
        'query': query, 'selected_category': category_id, 'selected_city': city,
    })


# ── EVENT DETAIL ───────────────────────────────────────────────────────────────
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    user_booked = False
    related = Event.objects.filter(is_active=True, date__gte=timezone.now()).exclude(pk=pk)
    if event.category:
        related = related.filter(category=event.category)
    related = related[:3]
    if request.user.is_authenticated:
        user_booked = Booking.objects.filter(user=request.user, event=event, status='confirmed').exists()
    return render(request, 'events/event_detail.html', {
        'event': event, 'user_booked': user_booked, 'related': related,
    })


# ── CHECKOUT ───────────────────────────────────────────────────────────────────
@login_required
def checkout(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    if event.is_sold_out:
        messages.error(request, 'Sorry, this event is sold out.')
        return redirect('event_detail', pk=pk)
    quantity = max(1, min(10, int(request.GET.get('qty', 1))))
    total = event.price * quantity
    return render(request, 'events/checkout.html', {'event': event, 'quantity': quantity, 'total': total})


# ── EMAIL TICKET ───────────────────────────────────────────────────────────────
def _send_ticket_email(booking):
    """Send a gorgeous HTML ticket confirmation email."""
    subject = f'🎟 Your Ticket — {booking.event.title}'
    html_body = render_to_string('emails/ticket_confirmation.html', {'booking': booking})
    plain_body = (
        f'Hi {booking.user.first_name or booking.user.username},\n\n'
        f'Your booking is CONFIRMED!\n\n'
        f'Event:   {booking.event.title}\n'
        f'Date:    {booking.event.date.strftime("%d %b %Y, %I:%M %p")}\n'
        f'Venue:   {booking.event.venue}, {booking.event.city}\n'
        f'Tickets: {booking.quantity}\n'
        f'Paid:    Rs.{booking.total_price}\n'
        f'Code:    {booking.confirmation_code}\n'
    )
    if hasattr(booking, 'payment'):
        plain_body += f'Txn ID:  {booking.payment.transaction_id}\n'
    plain_body += '\nSee you there!\n— TicketFlow Team'

    to_email = booking.user.email
    if to_email:
        msg = EmailMultiAlternatives(subject, plain_body, None, [to_email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=True)

    # Always print to console in dev
    print(f'\n{"="*60}')
    print(f'📧 TICKET EMAIL to: {to_email or "(no email set)"}')
    print(f'   Event:  {booking.event.title}')
    print(f'   Code:   {booking.confirmation_code}')
    print(f'{"="*60}\n')


# ── PROCESS PAYMENT ────────────────────────────────────────────────────────────
@login_required
def process_payment(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    if request.method != 'POST':
        return redirect('checkout', pk=pk)

    quantity = int(request.POST.get('quantity', 1))
    total = event.price * quantity
    card_number = request.POST.get('card_number', '').replace(' ', '')
    card_holder = request.POST.get('card_holder', '').strip()
    last4 = card_number[-4:] if len(card_number) >= 4 else '0000'

    if last4 == '0000':
        messages.error(request, '❌ Payment declined. Please try a different card.')
        return redirect('checkout', pk=pk)

    booking = Booking.objects.create(
        user=request.user, event=event,
        quantity=quantity, total_price=total, status='confirmed',
    )
    event.booked_seats += quantity
    event.save()

    txn_id = 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    Payment.objects.create(
        booking=booking, card_last4=last4, card_holder=card_holder,
        amount=total, status='success', transaction_id=txn_id,
    )

    # Re-fetch with payment relation attached
    booking.refresh_from_db()
    _send_ticket_email(booking)

    return redirect('payment_success', pk=booking.pk)


# ── PAYMENT SUCCESS ────────────────────────────────────────────────────────────
@login_required
def payment_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'events/payment_success.html', {'booking': booking})


# ── MY BOOKINGS ────────────────────────────────────────────────────────────────
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
        messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings')


# ── CALENDAR ───────────────────────────────────────────────────────────────────
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


# ── OTP HELPERS ────────────────────────────────────────────────────────────────
def _send_otp(email, purpose):
    OTPVerification.objects.filter(email=email, purpose=purpose, is_verified=False).delete()
    otp_obj = OTPVerification.objects.create(email=email, purpose=purpose)

    html_body = render_to_string('emails/otp_email.html', {
        'otp': otp_obj.otp, 'purpose': purpose, 'email': email
    })
    plain = f'Your TicketFlow OTP is: {otp_obj.otp}\n\nValid for 10 minutes. Do not share it with anyone.\n\n— TicketFlow'

    msg = EmailMultiAlternatives('🔐 Your TicketFlow OTP', plain, None, [email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)

    print(f'\n{"="*40}\n🔐 OTP for {email}: {otp_obj.otp}\n{"="*40}\n')
    return otp_obj


# ── REGISTER ───────────────────────────────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_otp':
            username  = request.POST.get('username', '').strip()
            email     = request.POST.get('email', '').strip()
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            errors = []
            if not username: errors.append('Username is required.')
            if User.objects.filter(username=username).exists(): errors.append('Username already taken.')
            if not email: errors.append('Email is required.')
            if User.objects.filter(email=email).exists(): errors.append('Email already registered.')
            if password1 != password2: errors.append('Passwords do not match.')
            if len(password1) < 8: errors.append('Password must be at least 8 characters.')
            if errors:
                return render(request, 'events/register.html', {
                    'step': 'form', 'errors': errors, 'username': username, 'email': email,
                })
            request.session['reg_username'] = username
            request.session['reg_email']    = email
            request.session['reg_password'] = password1
            request.session['reg_step']     = 'otp'
            _send_otp(email, 'register')
            return render(request, 'events/register.html', {'step': 'otp', 'email': email})

        elif action == 'verify_otp':
            email   = request.session.get('reg_email')
            entered = request.POST.get('otp', '').strip()
            otp_obj = OTPVerification.objects.filter(
                email=email, purpose='register', is_verified=False
            ).order_by('-created_at').first()

            if not otp_obj or otp_obj.is_expired:
                return render(request, 'events/register.html', {
                    'step': 'otp', 'email': email,
                    'otp_error': 'OTP expired. Please request a new one.',
                })
            if otp_obj.otp != entered:
                return render(request, 'events/register.html', {
                    'step': 'otp', 'email': email, 'otp_error': 'Invalid OTP. Try again.',
                })
            otp_obj.is_verified = True
            otp_obj.save()
            user = User.objects.create_user(
                username=request.session.get('reg_username'),
                email=email,
                password=request.session.get('reg_password'),
            )
            for k in ('reg_username', 'reg_email', 'reg_password', 'reg_step'):
                request.session.pop(k, None)
            login(request, user)
            messages.success(request, f'Welcome to TicketFlow, {user.username}! 🎉')
            return redirect('home')

        elif action == 'resend_otp':
            email = request.session.get('reg_email')
            if email:
                _send_otp(email, 'register')
                return render(request, 'events/register.html', {
                    'step': 'otp', 'email': email, 'otp_info': 'A new OTP has been sent.',
                })

    return render(request, 'events/register.html', {'step': 'form'})


# ── LOGIN WITH OTP ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_otp':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=username, password=password)
            if not user:
                return render(request, 'events/login.html', {
                    'step': 'form', 'error': 'Invalid username or password.', 'username': username,
                })
            request.session['login_user_id'] = user.pk
            email = user.email or ''
            if email:
                _send_otp(email, 'login')
            return render(request, 'events/login.html', {'step': 'otp', 'email': email or 'your email'})

        elif action == 'verify_otp':
            user_id = request.session.get('login_user_id')
            user = User.objects.filter(pk=user_id).first()
            if not user:
                return redirect('login_otp')
            entered = request.POST.get('otp', '').strip()
            otp_obj = OTPVerification.objects.filter(
                email=user.email, purpose='login', is_verified=False
            ).order_by('-created_at').first()
            if not otp_obj or otp_obj.is_expired:
                return render(request, 'events/login.html', {
                    'step': 'otp', 'email': user.email,
                    'otp_error': 'OTP expired. Please log in again.',
                })
            if otp_obj.otp != entered:
                return render(request, 'events/login.html', {
                    'step': 'otp', 'email': user.email, 'otp_error': 'Invalid OTP.',
                })
            otp_obj.is_verified = True
            otp_obj.save()
            request.session.pop('login_user_id', None)
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! 🎟')
            return redirect(request.GET.get('next', 'home'))

        elif action == 'resend_otp':
            user_id = request.session.get('login_user_id')
            user = User.objects.filter(pk=user_id).first()
            if user and user.email:
                _send_otp(user.email, 'login')
                return render(request, 'events/login.html', {
                    'step': 'otp', 'email': user.email, 'otp_info': 'New OTP sent.',
                })

    return render(request, 'events/login.html', {'step': 'form'})
