from django import forms

from .models import Brand, Category, Order, Product, ProductImage, ProductSpec


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "icon", "display_order"]
        labels = {"name": "نام دسته", "icon": "آیکون", "display_order": "ترتیب نمایش"}


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "logo"]
        labels = {"name": "نام برند", "logo": "لوگو"}


class ProductForm(forms.ModelForm):
    """فرم افزودن/ویرایش محصول — همون فیلدهایی که تو پنل ادمین فرانت پر می‌شن"""

    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "title",
            "description",
            "price",
            "discount_price",
            "main_image",
            "stock_quantity",
            "is_active",
        ]
        labels = {
            "category": "دسته‌بندی",
            "brand": "برند",
            "title": "عنوان محصول",
            "description": "توضیحات",
            "price": "قیمت (تومان)",
            "discount_price": "قیمت با تخفیف (تومان)",
            "main_image": "تصویر اصلی",
            "stock_quantity": "موجودی انبار",
            "is_active": "قابل نمایش در سایت",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        price = cleaned.get("price")
        discount_price = cleaned.get("discount_price")
        if discount_price and price and discount_price >= price:
            self.add_error("discount_price", "قیمت با تخفیف باید کمتر از قیمت اصلی باشه.")
        return cleaned


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "display_order"]
        labels = {"image": "تصویر", "alt_text": "متن جایگزین", "display_order": "ترتیب"}


class ProductSpecForm(forms.ModelForm):
    class Meta:
        model = ProductSpec
        fields = ["key", "value", "display_order"]
        labels = {"key": "عنوان مشخصه", "value": "مقدار", "display_order": "ترتیب"}


# فرم‌ست‌های داخل صفحه‌ی محصول (برای مدیریت گالری تصاویر و مشخصات فنی همراه با خود محصول)
ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage, form=ProductImageForm, extra=1, can_delete=True
)
ProductSpecFormSet = forms.inlineformset_factory(
    Product, ProductSpec, form=ProductSpecForm, extra=1, can_delete=True
)


class AddToCartForm(forms.Form):
    """فرم افزودن به سبد خرید — توی view، محصول از URL/context گرفته میشه، این فقط تعداد رو می‌گیره"""

    quantity = forms.IntegerField(min_value=1, initial=1, label="تعداد")


class OrderForm(forms.ModelForm):
    """فرم نهایی کردن خرید (checkout) — دقیقاً همون آدرس و شماره تماسی که تو فرانت گرفته میشه"""

    class Meta:
        model = Order
        fields = ["address", "phone"]
        labels = {"address": "آدرس کامل تحویل کالا", "phone": "شماره تماس"}
        widgets = {
            "address": forms.Textarea(
                attrs={"rows": 3, "placeholder": "استان، شهر، خیابان، پلاک، واحد..."}
            ),
            "phone": forms.TextInput(attrs={"placeholder": "09xxxxxxxxx"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not phone.isdigit() or len(phone) != 11 or not phone.startswith("09"):
            raise forms.ValidationError("شماره موبایل معتبر نیست (باید ۱۱ رقم باشه و با ۰۹ شروع بشه).")
        return phone