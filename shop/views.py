from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AddToCartForm, OrderForm
from .models import *

PRODUCTS_PER_PAGE = 12


def product_list(request):
    """لیست محصولات با فیلتر دسته‌بندی و جستجو — صفحه‌ی اصلی فروشگاه"""
    products = Product.objects.filter(is_active=True).select_related("category", "brand")
    categories = Category.objects.all()

    category_slug = request.GET.get("category", "").strip()
    search_query = request.GET.get("q", "").strip()

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "categories": categories,
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "current_category": category_slug,
        "search_query": search_query,
    }
    return render(request, "product.html", context)


def product_detail(request, slug):
    """صفحه‌ی جزئیات یک محصول، همراه با گالری تصاویر و مشخصات فنی"""
    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related("images", "specs"),
        slug=slug,
        is_active=True,
    )
    form = AddToCartForm(product=product)
    return render(request, "product_detail.html", {"product": product, "form": form})


def _get_cart(user):
    """سبد خرید کاربر رو برمی‌گردونه، اگه نداشت می‌سازه"""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    """نمایش سبد خرید — چون Cart به کاربر لاگین‌کرده وصله، این صفحه نیاز به لاگین داره"""
    cart = _get_cart(request.user)
    items = cart.items.select_related("product").all()
    return render(request, "cart_detail.html", {"cart": cart, "items": items})


@login_required
@require_POST
def cart_add(request, product_id):
    """افزودن یک محصول به سبد خرید (یا افزایش تعداد اگه از قبل تو سبد بود)"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    form = AddToCartForm(request.POST, product=product)

    if not form.is_valid():
        messages.error(request, "تعداد وارد شده معتبر نیست.")
        return redirect("product_detail", slug=product.slug)

    quantity = form.cleaned_data["quantity"]

    if not product.in_stock:
        messages.error(request, "این محصول در حال حاضر ناموجود است.")
        return redirect("product_detail", slug=product.slug)

    cart = _get_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity

    # بیشتر از موجودی انبار اجازه نده
    item.quantity = min(item.quantity, product.stock_quantity)
    item.save()

    messages.success(request, f"«{product.title}» به سبد خرید اضافه شد.")
    return redirect("cart_detail")


@login_required
@require_POST
def cart_update(request, item_id):
    """تغییر تعداد یک آیتم داخل سبد خرید"""
    cart = _get_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        messages.error(request, "تعداد وارد شده معتبر نیست.")
        return redirect("cart_detail")

    quantity = min(quantity, item.product.stock_quantity)

    if quantity <= 0:
        item.delete()
        messages.info(request, "محصول از سبد خرید حذف شد.")
    else:
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        messages.success(request, "تعداد سبد خرید به‌روزرسانی شد.")

    return redirect("cart_detail")


@login_required
@require_POST
def cart_remove(request, item_id):
    """حذف کامل یک آیتم از سبد خرید"""
    cart = _get_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.info(request, "محصول از سبد خرید حذف شد.")
    return redirect("cart_detail")


@login_required
def checkout(request):
    # ---------- سبد خرید ----------
    cart = Cart.objects.get_or_create(user=request.user)[0]

    items = list(
        cart.items
        .select_related("product")
        .all()
    )

    if not items:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect("cart_detail")

    # ============================================================
    #                       POST
    # ============================================================
    if request.method == "POST":

        # 👇👇👇 تغییر اصلی: user رو پاس می‌دیم
        form = OrderForm(request.POST, user=request.user)

        if form.is_valid():

            try:
                with transaction.atomic():

                    # قفل روی سبد کاربر
                    cart = (
                        Cart.objects
                        .select_for_update()
                        .get(user=request.user)
                    )

                    cart_items = list(
                        CartItem.objects
                        .select_for_update()
                        .select_related("product")
                        .filter(cart=cart)
                    )

                    if not cart_items:
                        messages.warning(request, "سبد خرید شما خالی است.")
                        return redirect("cart_detail")

                    # ---------- اعتبارسنجی محصولات + محاسبه مبلغ ----------
                    total_price = 0

                    for item in cart_items:
                        product = item.product

                        if not product.is_active:
                            messages.error(
                                request,
                                f"محصول «{product.title}» دیگر قابل خرید نیست.",
                            )
                            return redirect("cart_detail")

                        if item.quantity > product.stock_quantity:
                            messages.error(
                                request,
                                f"موجودی «{product.title}» کافی نیست.",
                            )
                            return redirect("cart_detail")

                        total_price += item.quantity * product.final_price

                    # ---------- ساخت سفارش ----------
                    order = form.save(commit=False)
                    order.user = request.user
                    order.status = Order.Status.PENDING
                    order.total_price = total_price
                    order.save()

                    # ---------- ساخت آیتم‌های سفارش ----------
                    OrderItem.objects.bulk_create([
                        OrderItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price_at_purchase=item.product.final_price,
                        )
                        for item in cart_items
                    ])

                    # ---------- کاهش موجودی ----------
                    for item in cart_items:
                        product = item.product
                        product.stock_quantity -= item.quantity
                        product.save(update_fields=["stock_quantity"])

                    # ---------- ساخت Payment ----------
                    payment = Payment.objects.create(
                        order=order,
                        amount=total_price,
                        status=Payment.Status.PENDING,
                    )

                    # ---------- خالی کردن سبد ----------
                    cart_items_qs = CartItem.objects.filter(cart=cart)
                    cart_items_qs.delete()

            except Exception as e:
                messages.error(request, "خطایی رخ داد. لطفاً دوباره تلاش کنید.")
                # برای دیباگ: print(e)
                return redirect("cart_detail")

            # بعد از commit موفق → مرحله پرداخت
            messages.success(request, "✓ سفارش شما با موفقیت ثبت شد.")
            return redirect("payment_start", order_id=order.id)

        else:
            # فرم خطا داره → پیام خطا نمایش بده
            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")

    # ============================================================
    #                       GET
    # ============================================================
    else:
        # 👇👇👇 تغییر اصلی: user رو پاس می‌دیم تا prefill بشه
        form = OrderForm(user=request.user)

    return render(
        request,
        "checkout.html",
        {
            "form": form,
            "items": items,
            "cart": cart,
        },
    )

@login_required
def order_success(request, order_id):
    """صفحه‌ی تایید بعد از ثبت موفق سفارش"""
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"), pk=order_id, user=request.user
    )
    return render(request, "order_success.html", {"order": order})


@login_required
def order_history(request):
    """تاریخچه‌ی سفارش‌های کاربر"""
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "order_history.html", {"orders": orders})


from django.db import transaction
from django.utils import timezone


def complete_successful_payment(
    order_id,
    transaction_id=None,
    ref_id=None,
    card_pan=None,
):
    with transaction.atomic():

        order = (
            Order.objects
            .select_for_update()
            .get(pk=order_id)
        )

        payment = (
            Payment.objects
            .select_for_update()
            .get(order=order)
        )

        if (
            order.status == Order.Status.PAID
            and payment.status == Payment.Status.SUCCESS
        ):
            return order

        items = list(
            order.items
            .select_related("product")
            .select_for_update()
            .all()
        )

        for item in items:

            product = (
                Product.objects
                .select_for_update()
                .get(pk=item.product_id)
            )

            if not product.is_active:
                raise ValueError(
                    f"محصول «{product.title}» "
                    "دیگر فعال نیست."
                )

            if item.quantity > product.stock_quantity:
                raise ValueError(
                    f"موجودی «{product.title}» کافی نیست."
                )

            product.stock_quantity -= item.quantity

            product.save(
                update_fields=[
                    "stock_quantity"
                ]
            )

        payment.status = Payment.Status.SUCCESS
        payment.transaction_id = transaction_id
        payment.ref_id = ref_id
        payment.card_pan = card_pan
        payment.paid_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "transaction_id",
                "ref_id",
                "card_pan",
                "paid_at",
                "updated_at",
            ]
        )

        order.status = Order.Status.PAID

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # پیدا کردن سبد کاربر
        cart = Cart.objects.filter(
            user=order.user
        ).first()

        if cart:
            CartItem.objects.filter(
                cart=cart
            ).delete()

    return order


@login_required
def payment_start(request, order_id):
    """
    شروع پرداخت سفارش
    """

    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    payment = get_object_or_404(
        Payment,
        order=order,
    )

    # سفارش قبلاً پرداخت شده
    if order.status == Order.Status.PAID:
        messages.info(
            request,
            "این سفارش قبلاً پرداخت شده است.",
        )

        return redirect(
            "order_success",
            order_id=order.id,
        )

    # پرداخت قبلی موفق بوده
    if payment.status == Payment.Status.SUCCESS:
        messages.info(
            request,
            "این سفارش قبلاً پرداخت شده است.",
        )

        return redirect(
            "order_success",
            order_id=order.id,
        )

    # =====================================================
    # فردا کد اتصال به درگاه اینجا قرار می‌گیرد.
    # =====================================================

    """
    نمونه ساختار:

    authority = gateway.request(
        amount=payment.amount,
        description=f"Order #{order.id}",
        callback_url=...
    )

    payment.authority = authority
    payment.save(
        update_fields=["authority"]
    )

    return redirect(
        gateway.payment_url(authority)
    )
    """

    messages.info(
        request,
        "درگاه پرداخت هنوز تنظیم نشده است.",
    )

    return redirect(
        "checkout"
    )

@login_required
def payment_callback(request, order_id):

    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    payment = get_object_or_404(
        Payment,
        order=order,
    )

    # -----------------------------------------
    # اگر کاربر پرداخت را لغو کرده
    # -----------------------------------------

    if request.GET.get("Status") != "OK":
        payment.status = Payment.Status.CANCELLED
        payment.error_message = "پرداخت توسط کاربر لغو شد."

        payment.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        messages.warning(
            request,
            "پرداخت لغو شد.",
        )

        return redirect(
            "checkout"
        )

    # -----------------------------------------
    # VERIFY واقعی درگاه
    # -----------------------------------------

    # result = zarinpal.verify(
    #     amount=payment.amount,
    #     authority=payment.authority,
    # )

    # -----------------------------------------
    # در صورت موفقیت
    # -----------------------------------------

    try:

        order = complete_successful_payment(
            order_id=order.id,
            transaction_id="...",
            ref_id="...",
            card_pan=None,
        )

    except ValueError as exc:

        payment.status = Payment.Status.FAILED
        payment.error_message = str(exc)

        payment.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )

        messages.error(
            request,
            "پرداخت انجام شد اما موجودی محصول کافی نیست. "
            "لطفاً با پشتیبانی تماس بگیرید.",
        )

        return redirect(
            "order_history"
        )

    messages.success(
        request,
        "پرداخت با موفقیت انجام شد.",
    )

    return redirect(
        "order_success",
        order_id=order.id,
    )