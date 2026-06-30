from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Room, Booking, Payment, StaffTask, CustomUser, StaffAttendance
from .forms import CustomUserCreationForm, BookingForm, RoomForm, StaffTaskForm, StaffForm
from datetime import date
from django.db.models import Sum

def home(request):
    # Fetch all rooms that are operational (available or booked, but not cleaning/maintenance if you had that)
    # Since we removed the 'booked' status logic, we should just get all rooms or filter by those not in maintenance.
    # For now, let's just get all rooms to be safe against previous 'booked' status.
    rooms = Room.objects.exclude(status='cleaning') 
    
    if request.method == 'GET':
        room_type = request.GET.get('type')
        max_price = request.GET.get('price')
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')

        if room_type:
            rooms = rooms.filter(room_type=room_type)
        if max_price:
            rooms = rooms.filter(price_per_night__lte=max_price)
            
        if check_in and check_out:
            try:
                # Find bookings that overlap with the requested range
                # Overlap condition: (StartA < EndB) and (EndA > StartB)
                occupied_room_ids = Booking.objects.filter(
                    check_in__lt=check_out,
                    check_out__gt=check_in
                ).values_list('room_id', flat=True)
                
                rooms = rooms.exclude(id__in=occupied_room_ids)
            except ValueError:
                pass # Handle invalid date format if necessary

    return render(request, 'home.html', {'rooms': rooms})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Decorators for role check
def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'staff' or request.user.role == 'admin'):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

@login_required
def guest_dashboard(request):
    bookings = Booking.objects.filter(guest=request.user)
    return render(request, 'guest_dashboard.html', {'bookings': bookings})

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.guest = request.user
            booking.room = room
            
            # Check availability logic
            conflicting_bookings = Booking.objects.filter(
                room=room,
                check_in__lt=booking.check_out,
                check_out__gt=booking.check_in
            )
            if conflicting_bookings.exists():
                 return render(request, 'book_room.html', {'room': room, 'form': form, 'error': 'Room is already booked for these dates'})

            booking.save()
            # room.status = 'booked'  <-- REMOVED: Do not globally mark room as booked. Availability depends on dates.
            # room.save()
            return redirect('booking_success', booking_id=booking.id)
        else:
            print("Form errors:", form.errors) # Debugging print
    else:
        # Pre-fill some data from user profile if available
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}",
            'email': request.user.email,
            'phone': request.user.phone,
            'check_in': request.GET.get('check_in'),
            'check_out': request.GET.get('check_out'),
        }
        form = BookingForm(initial=initial_data)

    return render(request, 'book_room.html', {'room': room, 'form': form})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    return render(request, 'booking_success.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    if booking.check_in > date.today():
         booking.room.status = 'available'
         booking.room.save()
         booking.delete()
    return redirect('guest_dashboard')

@login_required
def invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user == booking.guest or request.user.role in ['staff', 'admin']):
         return redirect('home')
    return render(request, 'invoice.html', {'booking': booking})


# Staff Views
@staff_required
def staff_dashboard(request):
    tasks = StaffTask.objects.filter(staff=request.user)
    rooms = Room.objects.all()
    return render(request, 'staff_dashboard.html', {'tasks': tasks, 'rooms': rooms})

@staff_required
def update_task_status(request, task_id):
    task = get_object_or_404(StaffTask, id=task_id, staff=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        task.task_status = status
        task.save()
    return redirect('staff_dashboard')

@staff_required
def update_room_status(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        room.status = status
        room.save()
    return redirect('staff_dashboard')


# Admin Views
@admin_required
def admin_dashboard(request):
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='booked').count()
    available_rooms = Room.objects.filter(status='available').count()
    total_revenue = Booking.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    bookings = Booking.objects.all()
    
    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'available_rooms': available_rooms,
        'total_revenue': total_revenue,
        'bookings': bookings
    }
    return render(request, 'admin_dashboard.html', context)

@admin_required
def manage_staff(request):
    if request.method == 'POST':
        if 'add_staff' in request.POST:
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            profession = request.POST.get('profession')
            phone = request.POST.get('phone')
            
            if email:
                if CustomUser.objects.filter(username=email).exists():
                    messages.error(request, f"A user with email {email} already exists.")
                else:
                    # Use email as username
                    user = CustomUser.objects.create_user(
                        username=email,
                        email=email,
                        password='StaffPassword@123', # Default password
                        first_name=first_name,
                        last_name=last_name,
                        role='staff',
                        profession=profession,
                        phone=phone
                    )
                    messages.success(request, f"Staff member {first_name} added successfully!")
                    return redirect('manage_staff')
            else:
                messages.error(request, "Email is required to add staff.")
        
        elif 'mark_attendance' in request.POST:
            staff_id = request.POST.get('staff_id')
            status = request.POST.get('status')
            staff_member = get_object_or_404(CustomUser, id=staff_id)
            StaffAttendance.objects.create(staff=staff_member, status=status)
            messages.success(request, f"Attendance marked for {staff_member.first_name}.")
            return redirect('manage_staff')

    staff_members = CustomUser.objects.filter(role='staff')
    today = date.today()
    
    # Calculate attendance for today
    attendance_records = {att.staff_id: att.status for att in StaffAttendance.objects.filter(date=today)}
    
    for staff in staff_members:
        staff.today_attendance = attendance_records.get(staff.id, 'Not Marked')

    form = CustomUserCreationForm()
    return render(request, 'manage_staff.html', {'staff_members': staff_members, 'form': form, 'today': today})

@admin_required
def edit_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, id=staff_id, role='staff')
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff details updated successfully.")
            return redirect('manage_staff')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'booking_form.html', {'form': form, 'title': f'Edit Staff: {staff.username}'})

@admin_required
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RoomForm()
    return render(request, 'booking_form.html', {'form': form, 'title': 'Add Room'}) 

@admin_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RoomForm(instance=room)
    return render(request, 'booking_form.html', {'form': form, 'title': 'Edit Room'})


@admin_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('admin_dashboard')

@admin_required
def mark_booking_paid(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.payment_status = True
    booking.save()
    return redirect('admin_dashboard')

def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'room_list.html', {'rooms': rooms})
