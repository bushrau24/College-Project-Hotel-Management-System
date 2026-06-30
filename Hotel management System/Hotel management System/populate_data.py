import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_horizon.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Room

User = get_user_model()

def create_admin():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='admin')
        print("Superuser 'admin' created with password 'admin123'")
    else:
        print("Superuser 'admin' already exists")

def create_rooms():
    rooms_data = [
        {'room_number': '101', 'room_type': 'single', 'price_per_night': 100.00, 'amenities': 'WiFi, TV, AC', 'status': 'available'},
        {'room_number': '102', 'room_type': 'single', 'price_per_night': 100.00, 'amenities': 'WiFi, TV, AC', 'status': 'available'},
        {'room_number': '201', 'room_type': 'double', 'price_per_night': 150.00, 'amenities': 'WiFi, TV, AC, Balcony', 'status': 'available'},
        {'room_number': '202', 'room_type': 'double', 'price_per_night': 150.00, 'amenities': 'WiFi, TV, AC, Balcony', 'status': 'available'},
        {'room_number': '301', 'room_type': 'suite', 'price_per_night': 300.00, 'amenities': 'WiFi, TV, AC, Balcony, Mini Bar, Sea View', 'status': 'available'},
    ]

    for data in rooms_data:
        if not Room.objects.filter(room_number=data['room_number']).exists():
            Room.objects.create(**data)
            print(f"Room {data['room_number']} created")
        else:
            print(f"Room {data['room_number']} already exists")

if __name__ == '__main__':
    print("Populating database...")
    create_admin()
    create_rooms()
    print("Database populated successfully!")
