from django.contrib import admin
from .models import Employee, Supplier, Product, Attendance, EmployeeProfile, DailyWork
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

admin.site.register(Employee)
admin.site.register(Supplier)
admin.site.register(Product)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('public_id', 'user', 'phone', 'designation')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'status', 'timestamp')
    list_filter = ('status',)

@admin.register(DailyWork)
class DailyWorkAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'product_count')
    list_filter = ('date',)

