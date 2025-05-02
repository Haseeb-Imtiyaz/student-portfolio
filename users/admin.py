from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, EmployerProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Account Type', {'fields': ('user_type',)}),
        ('Permissions', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'course', 'year_of_study')
    search_fields = ('user__username', 'user__email', 'college__name', 'course__name')
    list_filter = ('course', 'year_of_study')

class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'industry', 'location')
    search_fields = ('user__username', 'user__email', 'company_name', 'industry')
    list_filter = ('industry', 'company_size')

admin.site.register(User, CustomUserAdmin)
admin.site.register(EmployerProfile, EmployerProfileAdmin)
