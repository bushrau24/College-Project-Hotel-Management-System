from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Room(models.Model):
    ROOM_TYPES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    )
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('cleaning', 'Cleaning'),
    )
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def __str__(self):
        return f"{self.room_number} - {self.room_type}"

class Booking(models.Model):
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New Fields
    full_name = models.CharField(max_length=255, verbose_name="Guest Name")
    email = models.EmailField(verbose_name="Contact Email")
    phone = models.CharField(max_length=20, verbose_name="Contact Phone")
    address = models.TextField(blank=True, null=True)
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    id_proof_type = models.CharField(max_length=50, choices=[('aadhar', 'Aadhar Card'), ('passport', 'Passport'), ('dl', 'Driving License')], default='aadhar')
    id_proof_number = models.CharField(max_length=50)
    special_requests = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.total_amount:
            # Ensure check_in and check_out are date objects
            from datetime import datetime, date
            
            c_in = self.check_in
            c_out = self.check_out

            if isinstance(c_in, str):
                c_in = datetime.strptime(c_in, '%Y-%m-%d').date()
            if isinstance(c_out, str):
                c_out = datetime.strptime(c_out, '%Y-%m-%d').date()

            days = (c_out - c_in).days
            if days < 1: 
                days = 1
            self.total_amount = days * self.room.price_per_night
            
            # Update the fields back to correct types if needed (though Django handles it mostly)
            self.check_in = c_in
            self.check_out = c_out

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} - {self.guest.username}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id}"

class StaffTask(models.Model):
    TASK_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'staff'})
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    task_description = models.TextField()
    task_status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task for {self.staff.username} - {self.room.room_number}"


class StaffAttendance(models.Model):
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'staff'}, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')], default='present')
    
    class Meta:
        unique_together = ('staff', 'date')

    def __str__(self):
        return f"{self.staff.username} - {self.date} - {self.status}"
