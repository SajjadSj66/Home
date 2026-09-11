from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Support


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'mobile', 'first_name', 'last_name',
        'customer_level', 'points', 'is_active', 'is_verified', 'date_joined',
    )
    list_filter = ('customer_level', 'gender', 'is_active', 'is_verified', 'is_staff')
    search_fields = ('mobile', 'first_name', 'last_name', 'email', 'national_code')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        (('اطلاعات شخصی'), {
            'fields': (
                'first_name', 'last_name', 'email',
                'national_code', 'birth_date', 'gender',
                'city', 'avatar',
            )
        }),
        (('باشگاه مشتریان'), {
            'fields': ('points', 'customer_level')
        }),
        (('وضعیت حساب'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions')
        }),
        (('تاریخ‌ها'), {
            'fields': ('last_login', 'date_joined', 'updated_at')
        }),
    )

    readonly_fields = ('date_joined', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2'),
        }),
    )

@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ("full_name", "subject", "status", "created_at")
    search_fields = ("phone", "subject", "message")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "مدیریت تیکت‌ها"
