from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MobileForm, OTPVerificationForm, SupportForm
from .models import *
from .utils import *
from shop.models import Category, Product
import random
import logging
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.urls import reverse


def index(request):
    categories = Category.objects.all()[:8]
    latest_products = Product.objects.filter(is_active=True).select_related("category", "brand").order_by("-created_at")[:8]
    discounted_products = Product.objects.filter(is_active=True, discount_price__isnull=False).select_related("category", "brand").order_by("-created_at")[:8]
    popular_products = Product.objects.filter(is_active=True, rating__gt=0).select_related("category", "brand").order_by("-rating", "-created_at")[:4]

    return render(request, "index.html", {
        "categories": categories,
        "latest_products": latest_products,
        "discounted_products": discounted_products,
        "popular_products": popular_products,
    })


logger = logging.getLogger(__name__)


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    pending_user_id = request.session.get("pending_user_id")

    if pending_user_id:
        user = User.objects.filter(id=pending_user_id).first()
        if not user:
            request.session.pop("pending_user_id", None)
            return render(request, "register.html", {"form": MobileForm(), "step": "mobile"})

        latest_otp = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not latest_otp or latest_otp.is_expired():
            request.session.pop("pending_user_id", None)
            return render(request, "register.html", {"form": MobileForm(), "step": "mobile"})

        cooldown_seconds = int((latest_otp.created_at + timedelta(minutes=2) - timezone.now()).total_seconds())
        cooldown_seconds = max(0, cooldown_seconds)

        if request.method == "POST":
            if "resend" in request.POST or "resend_otp" in request.POST:
                latest = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
                if latest and not latest.is_expired():
                    remaining = int((latest.created_at + timedelta(minutes=2) - timezone.now()).total_seconds())
                    remaining = max(0, remaining)
                    messages.info(request, f"کد قبلی هنوز معتبر است. لطفاً {remaining} ثانیه صبر کنید.")
                    return redirect(reverse("register"))

                PhoneOTP.objects.filter(user=user, is_used=False).update(is_used=True)
                otp_code = f"{random.randint(0, 999999):06d}"
                try:
                    PhoneOTP.objects.create(user=user, otp=otp_code)
                    send_otp_code(user.mobile, otp_code)
                    messages.success(request, "کد جدید ارسال شد.")
                except Exception as e:
                    logger.exception("Failed to send OTP to %s: %s", user.mobile, e)
                    messages.error(request, "ارسال کد با خطا مواجه شد. لطفاً بعداً تلاش کنید.")
                return redirect(reverse("register"))

            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                otp_entered = form.cleaned_data["otp"]
                otp_obj = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()

                if not otp_obj:
                    messages.error(request, "کدی برای این شماره ارسال نشده است.")
                    return redirect(reverse("register"))

                if otp_obj.is_expired():
                    otp_obj.is_used = True
                    otp_obj.save(update_fields=["is_used"])
                    request.session.pop("pending_user_id", None)
                    messages.error(request, "کد تایید منقضی شده است. لطفاً دوباره شماره خود را وارد کنید.")
                    return redirect(reverse("register"))

                if otp_obj.otp == otp_entered:
                    otp_obj.is_used = True
                    otp_obj.save(update_fields=["is_used"])
                    user.is_active = True
                    if hasattr(user, "is_verified"):
                        user.is_verified = True
                        user.save(update_fields=["is_active", "is_verified"])
                    else:
                        user.save(update_fields=["is_active"])
                    request.session.pop("pending_user_id", None)
                    login(request, user)
                    return redirect("dashboard")

                messages.error(request, "کد وارد شده اشتباه است.")
                return redirect(reverse("register"))

        return render(request, "register.html", {
            "form": OTPVerificationForm(),
            "step": "otp",
            "mobile": user.mobile,
            "cooldown_seconds": cooldown_seconds,
        })

    if request.method == "POST":
        form = MobileForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data["mobile"]
            user, _ = User.objects.get_or_create(mobile=mobile, defaults={"is_active": False})
            otp_obj = PhoneOTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
            if otp_obj and not otp_obj.is_expired():
                messages.info(request, "کد قبلی هنوز معتبر است.")
                request.session["pending_user_id"] = user.id
                return redirect(reverse("register"))

            PhoneOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            otp_code = f"{random.randint(0, 999999):06d}"
            try:
                PhoneOTP.objects.create(user=user, otp=otp_code)
                send_otp_code(mobile, otp_code)
                print(otp_code)
                messages.success(request, "کد تایید ارسال شد.")
            except Exception as e:
                logger.exception("Failed to send OTP to %s: %s", mobile, e)
                messages.error(request, "ارسال کد با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.")
                return redirect(reverse("register"))
            request.session["pending_user_id"] = user.id
            return redirect(reverse("register"))
    else:
        form = MobileForm()

    return render(request, "register.html", {"form": form, "step": "mobile"})


@login_required
def dashboard_view(request):
    orders = request.user.orders.select_related("user")
    return render(request, "dashboard.html", {"orders": orders})


@login_required
def support(request):
    if request.method == "POST":
        form = SupportForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": "/dashboard/"})
            return redirect("dashboard")
    else:
        form = SupportForm()
    return render(request, "ticket.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


def about(request):
    return render(request, "darbare.html")


def about_plans(request):
    return render(request, "about_plans.html")


def blog(request):
    return render(request, "blog.html")


def security(request):
    return render(request, "gavanin.html")
