from django import forms
from .models import User, Support
import re

# ----------------------------
# فرم ورود شماره موبایل
# ----------------------------
class MobileForm(forms.Form):
    mobile = forms.CharField(
        max_length=20,
        label="شماره موبایل",
        widget=forms.TextInput(attrs={
            'placeholder': 'شماره موبایل خود را وارد کنید',
            'class': 'form-control',  # اختیاری، برای استایل دادن
            'autocomplete': 'tel'
        })
    )

    def clean_mobile(self):
        m = self.cleaned_data["mobile"].strip()
        # تبدیل ارقام فارسی به انگلیسی + حذف غیرعددی‌ها
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        for i, d in enumerate(persian_digits):
            m = m.replace(d, str(i))
        m = re.sub(r"\D", "", m)
        # نرمال‌سازی رایج ایران
        if m.startswith("98") and len(m) == 12:
            m = "0" + m[2:]
        if not re.fullmatch(r"09\d{9}", m):
            raise forms.ValidationError("شماره موبایل نامعتبر است.")
        return m

# ----------------------------
# فرم تایید کد OTP
# ----------------------------
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        label='کد تایید',
        widget=forms.TextInput(attrs={
            'placeholder': '******',
            'class': 'form-control',
            'maxlength': 6,
            'autocomplete': 'off'
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data['otp']
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("کد تایید فقط باید شامل 6 عدد باشد")
        return otp

# ----------------------------
# فرم پشتیبانی
# ----------------------------
class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['subject', 'full_name', 'phone', 'email', 'department', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام و نام خانوادگی'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره موبایل یا تلفن'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'پیام خود را وارد کنید..',
                'rows': 4
            }),
        }
