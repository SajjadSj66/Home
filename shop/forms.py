from django import forms

from .models import (
    Brand,
    Category,
    Order,
    Product,
    ProductImage,
    ProductSpec,
)


# =========================================================
# Category
# =========================================================

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "icon", "display_order"]

        labels = {
            "name": "نام دسته",
            "icon": "آیکون",
            "display_order": "ترتیب نمایش",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً لوازم پخت و پز",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً fa-solid fa-pot-food",
                }
            ),
            "display_order": forms.NumberInput(
                attrs={
                    "min": 0,
                }
            ),
        }


# =========================================================
# Brand
# =========================================================

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "logo"]

        labels = {
            "name": "نام برند",
            "logo": "لوگو",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً بوش",
                }
            ),
        }


# =========================================================
# Product
# =========================================================

class ProductForm(forms.ModelForm):
    """
    فرم ایجاد / ویرایش محصول
    """

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
            "price": "قیمت اصلی (تومان)",
            "discount_price": "قیمت با تخفیف (تومان)",
            "main_image": "تصویر اصلی",
            "stock_quantity": "موجودی انبار",
            "is_active": "قابل نمایش در سایت",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "نام محصول را وارد کنید",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "توضیحات کامل محصول...",
                }
            ),

            "price": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                    "placeholder": "مثلاً 12500000",
                }
            ),

            "discount_price": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                    "placeholder": "در صورت داشتن تخفیف",
                }
            ),

            "stock_quantity": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                }
            ),

            "is_active": forms.CheckboxInput(),
        }

    def clean(self):
        cleaned_data = super().clean()

        price = cleaned_data.get("price")
        discount_price = cleaned_data.get("discount_price")

        if price is not None and price < 0:
            self.add_error(
                "price",
                "قیمت نمی‌تواند منفی باشد."
            )

        if discount_price is not None and discount_price < 0:
            self.add_error(
                "discount_price",
                "قیمت تخفیف نمی‌تواند منفی باشد."
            )

        if (
            price is not None
            and discount_price is not None
            and discount_price >= price
        ):
            self.add_error(
                "discount_price",
                "قیمت با تخفیف باید کمتر از قیمت اصلی باشد."
            )

        return cleaned_data


# =========================================================
# Product Image
# =========================================================

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage

        fields = [
            "image",
            "alt_text",
            "display_order",
        ]

        labels = {
            "image": "تصویر",
            "alt_text": "متن جایگزین",
            "display_order": "ترتیب",
        }

        widgets = {
            "alt_text": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً نمای جلوی محصول",
                }
            ),
            "display_order": forms.NumberInput(
                attrs={
                    "min": 0,
                }
            ),
        }


# =========================================================
# Product Specification
# =========================================================

class ProductSpecForm(forms.ModelForm):
    class Meta:
        model = ProductSpec

        fields = [
            "key",
            "value",
            "display_order",
        ]

        labels = {
            "key": "عنوان مشخصه",
            "value": "مقدار",
            "display_order": "ترتیب",
        }

        widgets = {
            "key": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً توان مصرفی",
                }
            ),
            "value": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً ۱۸۰۰ وات",
                }
            ),
            "display_order": forms.NumberInput(
                attrs={
                    "min": 0,
                }
            ),
        }


# =========================================================
# Inline Formsets
# =========================================================

ProductImageFormSet = forms.inlineformset_factory(
    parent_model=Product,
    model=ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=True,
)

ProductSpecFormSet = forms.inlineformset_factory(
    parent_model=Product,
    model=ProductSpec,
    form=ProductSpecForm,
    extra=1,
    can_delete=True,
)


# =========================================================
# Add To Cart
# =========================================================

class AddToCartForm(forms.Form):
    """
    فرم افزودن محصول به سبد خرید.

    در view محصول را به فرم پاس بده:
        form = AddToCartForm(product=product)
    """

    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="تعداد",
        widget=forms.NumberInput(
            attrs={
                "min": 1,
                "step": 1,
            }
        ),
    )

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

        if product is not None:
            self.fields["quantity"].widget.attrs["max"] = product.stock_quantity

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if self.product is None:
            return quantity

        if not self.product.is_active:
            raise forms.ValidationError(
                "این محصول در حال حاضر قابل خرید نیست."
            )

        if self.product.stock_quantity <= 0:
            raise forms.ValidationError(
                "این محصول در حال حاضر موجود نیست."
            )

        if quantity > self.product.stock_quantity:
            raise forms.ValidationError(
                f"حداکثر تعداد قابل خرید: {self.product.stock_quantity}"
            )

        return quantity


# =========================================================
# Order / Checkout
# =========================================================

class OrderForm(forms.ModelForm):
    """
    فرم نهایی کردن خرید
    """

    class Meta:
        model = Order

        fields = [
            "address",
            "phone",
        ]

        labels = {
            "address": "آدرس کامل تحویل کالا",
            "phone": "شماره تماس",
        }

        widgets = {
            "address": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "استان، شهر، خیابان، پلاک، واحد..."
                    ),
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "09xxxxxxxxx",
                    "inputmode": "tel",
                    "maxlength": "11",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        # تبدیل اعداد فارسی و عربی به انگلیسی
        translation_table = str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )

        phone = phone.translate(translation_table)

        # حذف فاصله
        phone = phone.replace(" ", "")

        if (
            not phone.isdigit()
            or len(phone) != 11
            or not phone.startswith("09")
        ):
            raise forms.ValidationError(
                "شماره موبایل معتبر نیست. "
                "شماره باید ۱۱ رقم باشد و با ۰۹ شروع شود."
            )

        return phone