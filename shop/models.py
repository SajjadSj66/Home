from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """دسته‌بندی لوازم آشپزخانه (قابلمه، سرخ‌کن، آبمیوه‌گیری، اجاق گاز و ...)"""

    name = models.CharField("نام دسته", max_length=100, unique=True)
    slug = models.SlugField("اسلاگ", max_length=110, unique=True, blank=True)
    icon = models.CharField("آیکون (اختیاری)", max_length=50, blank=True)
    display_order = models.PositiveSmallIntegerField("ترتیب نمایش", default=0)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """برند سازنده (مثلاً پارس‌خزر، فلر، بوش و ...)"""

    name = models.CharField("نام برند", max_length=100, unique=True)
    slug = models.SlugField("اسلاگ", max_length=110, unique=True, blank=True)
    logo = models.ImageField("لوگو", upload_to="brands/", blank=True, null=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    """یک کالای لوازم آشپزخانه (مثلاً سرخ‌کن، آبمیوه‌گیری، قابلمه‌ست و ...)"""

    category = models.ForeignKey(
        Category, verbose_name="دسته‌بندی", related_name="products", on_delete=models.PROTECT
    )
    brand = models.ForeignKey(
        Brand, verbose_name="برند", related_name="products",
        on_delete=models.SET_NULL, null=True, blank=True,
    )

    title = models.CharField("عنوان محصول", max_length=200)
    slug = models.SlugField("اسلاگ", max_length=220, unique=True, blank=True)
    description = models.TextField("توضیحات", blank=True)

    price = models.PositiveBigIntegerField("قیمت (تومان)")
    discount_price = models.PositiveBigIntegerField(
        "قیمت با تخفیف (تومان)", null=True, blank=True,
        help_text="اگه محصول تخفیف نداره، خالی بذار.",
    )

    main_image = models.ImageField("تصویر اصلی", upload_to="products/", blank=True, null=True)

    stock_quantity = models.PositiveIntegerField("موجودی انبار", default=0)
    rating = models.DecimalField(
        "امتیاز محبوبیت", max_digits=2, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    is_active = models.BooleanField("قابل نمایش در سایت", default=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["category", "is_active"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def final_price(self):
        """قیمتی که باید تو فرانت نشون داده بشه (اگه تخفیف داشت، همون؛ وگرنه قیمت اصلی)"""
        return self.discount_price or self.price


class ProductImage(models.Model):
    """تصاویر اضافه برای گالری محصول (علاوه بر تصویر اصلی)"""

    product = models.ForeignKey(Product, verbose_name="محصول", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField("تصویر", upload_to="products/gallery/")
    alt_text = models.CharField("متن جایگزین", max_length=150, blank=True)
    display_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ["display_order"]

    def __str__(self):
        return f"تصویر {self.product.title}"


class ProductSpec(models.Model):
    """مشخصات فنی محصول به‌صورت کلید/مقدار (دقیقا همون چیزی که تو برگه‌ی مشخصات فرانت نشون داده میشه)"""

    product = models.ForeignKey(Product, verbose_name="محصول", related_name="specs", on_delete=models.CASCADE)
    key = models.CharField("عنوان مشخصه", max_length=80, help_text="مثلاً: توان مصرفی، ظرفیت، جنس بدنه")
    value = models.CharField("مقدار", max_length=200, help_text="مثلاً: ۱۸۰۰ وات، ۵ لیتر، استیل ضدزنگ")
    display_order = models.PositiveSmallIntegerField("ترتیب", default=0)

    class Meta:
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.key}: {self.value}"


class Order(models.Model):
    """سفارش ثبت‌شده توسط کاربر (مدل User از اپ users خودت میاد)"""

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        PAID = "paid", "پرداخت‌شده"
        PROCESSING = "processing", "در حال آماده‌سازی"
        SHIPPED = "shipped", "ارسال‌شده"
        DELIVERED = "delivered", "تحویل‌شده"
        CANCELLED = "cancelled", "لغوشده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="کاربر", related_name="orders", on_delete=models.CASCADE
    )
    address = models.TextField("آدرس تحویل")
    phone = models.CharField("شماره تماس", max_length=15)
    status = models.CharField("وضعیت سفارش", max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.PositiveBigIntegerField("مبلغ کل (تومان)", default=0)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"سفارش #{self.id} — {self.user}"

    def recalculate_total(self):
        """جمع مبلغ آیتم‌ها رو دوباره حساب می‌کنه و ذخیره می‌کنه (بعد از اضافه/حذف آیتم صداش بزن)"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    """هر ردیفِ داخل یک سفارش (یک محصول + تعدادش)"""

    order = models.ForeignKey(Order, verbose_name="سفارش", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name="محصول", related_name="order_items", on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField("تعداد", default=1)
    price_at_purchase = models.PositiveBigIntegerField(
        "قیمت لحظه‌ی خرید (تومان)",
        help_text="قیمت محصول رو موقع ثبت سفارش اینجا کپی کن تا بعداً با تغییر قیمت محصول جابه‌جا نشه.",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase


class Cart(models.Model):
    """سبد خرید فعال هر کاربر — یک کاربر همیشه یک سبد داره (تا وقتی تسویه بشه و سفارش بسازه)"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name="کاربر", related_name="cart", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین به‌روزرسانی", auto_now=True)

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"سبد خرید {self.user}"

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    """هر ردیف داخل سبد خرید (یک محصول + تعدادش). بعد از تسویه، این‌ها به OrderItem تبدیل می‌شن."""

    cart = models.ForeignKey(Cart, verbose_name="سبد خرید", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name="محصول", related_name="cart_items", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField("تعداد", default=1)
    added_at = models.DateTimeField("تاریخ افزودن", auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ("cart", "product")  # هر محصول فقط یک ردیف تو سبد داره، تعداد زیاد میشه نه ردیف تکراری

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"

    @property
    def subtotal(self):
        return self.quantity * self.product.final_price