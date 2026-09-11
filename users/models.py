from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


# Create your models here.
mobile_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message='شماره موبایل باید با ۰۹ شروع شده و ۱۱ رقم باشد.'
)

national_code_validator = RegexValidator(
    regex=r'^\d{10}$',
    message='کد ملی باید ۱۰ رقم باشد.'
)


class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError('شماره موبایل الزامی است')

        mobile = self.normalize_email(mobile) if '@' in mobile else mobile
        extra_fields.setdefault('is_active', False)

        user = self.model(mobile=mobile, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser باید is_staff=True باشد')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser باید is_superuser=True باشد')

        return self.create_user(mobile, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Gender(models.TextChoices):
        MALE   = 'male',   _('مرد')
        FEMALE = 'female', _('زن')
        OTHER  = 'other',  _('سایر')

    class CustomerLevel(models.TextChoices):
        BRONZE  = 'bronze',  _('برنزی')
        SILVER  = 'silver',  _('نقره‌ای')
        GOLD    = 'gold',    _('طلایی')
        DIAMOND = 'diamond', _('الماس')

    # ---------- احراز هویت ----------
    mobile = models.CharField(
        _('شماره موبایل'),
        max_length=11,
        unique=True,
        validators=[mobile_validator],
    )
    email = models.EmailField(_('ایمیل'), blank=True, null=True)

    # ---------- اطلاعات شخصی ----------
    first_name = models.CharField(_('نام'), max_length=100, blank=True)
    last_name = models.CharField(_('نام خانوادگی'), max_length=100, blank=True)
    national_code = models.CharField(
        _('کد ملی'),
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        validators=[national_code_validator],
    )
    birth_date = models.DateField(_('تاریخ تولد'), blank=True, null=True)
    gender = models.CharField(
        _('جنسیت'),
        max_length=10,
        choices=Gender.choices,
        blank=True,
    )
    city = models.CharField(_('شهر'), max_length=50, blank=True)
    avatar = models.ImageField(
        _('تصویر پروفایل'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
    )

    # ---------- وضعیت حساب ----------
    is_active = models.BooleanField(_('فعال'), default=False)
    is_verified = models.BooleanField(_('تأیید شده'), default=False)
    is_staff = models.BooleanField(_('کارمند'), default=False)

    # ---------- باشگاه مشتریان ----------
    points = models.PositiveIntegerField(_('امتیاز'), default=0)
    customer_level = models.CharField(
        _('سطح مشتری'),
        max_length=10,
        choices=CustomerLevel.choices,
        default=CustomerLevel.BRONZE,
    )

    # ---------- تاریخ‌ها ----------
    date_joined = models.DateTimeField(_('تاریخ عضویت'), default=timezone.now)
    updated_at = models.DateTimeField(_('آخرین بروزرسانی'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ['-date_joined']

    def __str__(self):
        return self.mobile

    # ---------- متدها ----------
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.mobile

    def get_short_name(self):
        return self.first_name or self.mobile

    @property
    def first_letter(self):
        """حرف اول اسم برای آواتار پیش‌فرض در HTML"""
        return (self.first_name or self.mobile)[0]

    @property
    def orders_count(self):
        """تعداد سفارش‌ها - با related_name='orders' روی مدل Order"""
        return getattr(self, 'orders', None).count() if hasattr(self, 'orders') else 0

    @property
    def addresses_count(self):
        return getattr(self, 'addresses', None).count() if hasattr(self, 'addresses') else 0

    @property
    def profile_completion(self):
        """درصد تکمیل پروفایل برای نوار پیشرفت داشبورد"""
        fields = [
            self.first_name,
            self.last_name,
            self.email,
            self.national_code,
            self.birth_date,
            self.gender,
            self.city,
            self.avatar,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    @property
    def level_display(self):
        """متن نمایشی سطح مشتری برای HTML"""
        return self.get_customer_level_display()

    def update_customer_level(self, commit=True):
        if self.points >= 1000:
            self.customer_level = self.CustomerLevel.DIAMOND
        elif self.points >= 500:
            self.customer_level = self.CustomerLevel.GOLD
        elif self.points >= 200:
            self.customer_level = self.CustomerLevel.SILVER
        else:
            self.customer_level = self.CustomerLevel.BRONZE
        if commit:
            self.save(update_fields=['customer_level'])

class PhoneOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"{self.user.mobile} - {self.otp}"


class Support(models.Model):
    DEPARTMENTS = [
        ('support', 'پشتیبانی فنی'),
        ('finance', 'امور مالی'),
        ('orders', 'سفارش‌ها'),
    ]

    STATUS_CHOICES = (
        ('open', 'باز'),
        ('in_progress', 'در حال بررسی'),
        ('closed', 'بسته شده'),
    )

    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی", blank=True)
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    phone = models.CharField(max_length=11, verbose_name="موبایل")
    email = models.EmailField(default='')
    message = models.TextField(verbose_name="متن تیکت")
    department = models.CharField(max_length=20, choices=DEPARTMENTS, default='support')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
