from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Guest
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('rooms/', views.room_list, name='room_list'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.guest_dashboard, name='guest_dashboard'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('invoice/<int:booking_id>/', views.invoice, name='invoice'),

    # Staff
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/update-task/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('staff/update-room/<int:room_id>/', views.update_room_status, name='update_room_status'),

    # Admin
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/rooms/add/', views.add_room, name='add_room'),
    path('custom-admin/rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('custom-admin/rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('custom-admin/bookings/mark-paid/<int:booking_id>/', views.mark_booking_paid, name='mark_booking_paid'),
    path('custom-admin/staff/', views.manage_staff, name='manage_staff'),
    path('custom-admin/staff/edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
]
