from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AddToCartForm, OrderForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product

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
    form = AddToCartForm()
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
    form = AddToCartForm(request.POST)

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
    """گرفتن آدرس/تلفن، ساخت Order از روی آیتم‌های سبد، و خالی کردن سبد بعد از ثبت موفق"""
    cart = _get_cart(request.user)
    items = list(cart.items.select_related("product").all())

    if not items:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect("cart_detail")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # درست قبل از ثبت نهایی، دوباره موجودی رو چک کن (ممکنه در این فاصله تغییر کرده باشه)
            for item in items:
                if item.quantity > item.product.stock_quantity:
                    messages.error(
                        request,
                        f"موجودی «{item.product.title}» کافی نیست "
                        f"(فقط {item.product.stock_quantity} عدد باقی مانده).",
                    )
                    return redirect("cart_detail")

            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.save()

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price_at_purchase=item.product.final_price,
                    )
                    item.product.stock_quantity -= item.quantity
                    item.product.save(update_fields=["stock_quantity"])

                order.recalculate_total()
                cart.clear()

            return redirect("order_success", order_id=order.id)
    else:
        form = OrderForm()

    return render(request, "checkout.html", {"form": form, "items": items, "cart": cart})


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