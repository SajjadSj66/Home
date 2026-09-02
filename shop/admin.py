from django.contrib import admin

from .models import (
    Brand,
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductSpec,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    list_editable = ("display_order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "display_order")


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1
    fields = ("key", "value", "display_order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "brand",
        "price",
        "discount_price",
        "stock_quantity",
        "in_stock_badge",
        "rating",
        "is_active",
    )
    list_filter = ("category", "brand", "is_active")
    search_fields = ("title", "description")
    list_editable = ("stock_quantity", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("brand",)
    inlines = [ProductImageInline, ProductSpecInline]
    fieldsets = (
        (None, {"fields": ("category", "brand", "title", "slug", "description")}),
        ("قیمت و موجودی", {"fields": ("price", "discount_price", "stock_quantity", "rating")}),
        ("نمایش", {"fields": ("main_image", "is_active")}),
    )

    @admin.display(boolean=True, description="موجود")
    def in_stock_badge(self, obj):
        return obj.in_stock


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price_at_purchase", "subtotal")
    readonly_fields = ("subtotal",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "phone", "address")
    list_editable = ("status",)
    readonly_fields = ("total_price", "created_at", "updated_at")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"

    actions = ["recalculate_totals"]

    @admin.action(description="محاسبه‌ی مجدد مبلغ کل سفارش‌های انتخاب‌شده")
    def recalculate_totals(self, request, queryset):
        for order in queryset:
            order.recalculate_total()


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ("product", "quantity", "subtotal", "added_at")
    readonly_fields = ("subtotal", "added_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_quantity", "total_price", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]