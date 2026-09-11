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
    """فرم تسویه حساب — با prefill از اطلاعات کاربر لاگین‌شده"""

    class Meta:
        model = Order
        fields = [
            "recipient_first_name",
            "recipient_last_name",
            "phone",
            "address",
            "postal_code",
            "referral_source",
        ]
        widgets = {
            "recipient_first_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "مثلاً: سارا",
                "autocomplete": "given-name",
            }),
            "recipient_last_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "مثلاً: محمدی",
                "autocomplete": "family-name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "09123456789",
                "inputmode": "numeric",
                "autocomplete": "tel",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 4,
                "placeholder": "استان، شهر، خیابان، کوچه، پلاک، واحد…",
                "autocomplete": "street-address",
            }),
            "postal_code": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "۱۰ رقم",
                "maxlength": "10",
                "inputmode": "numeric",
                "autocomplete": "postal-code",
            }),
            "referral_source": forms.Select(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # 👇 prefill از کاربر لاگین‌شده (فقط وقتی فرم جدید باز می‌شه، نه در POST)
        if user and not self.is_bound:
            self.fields["recipient_first_name"].initial = user.first_name
            self.fields["recipient_last_name"].initial = user.last_name
            self.fields["phone"].initial = user.mobile

    # ---------- اعتبارسنجی ----------
    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone.isdigit() or not phone.startswith("09") or len(phone) != 11:
            raise forms.ValidationError(
                "شماره موبایل باید با ۰۹ شروع شده و ۱۱ رقم باشد."
            )
        return phone

    def clean_postal_code(self):
        code = self.cleaned_data.get("postal_code", "").strip()
        if code and (not code.isdigit() or len(code) != 10):
            raise forms.ValidationError("کد پستی باید ۱۰ رقم عددی باشد.")
        return code

    def clean_recipient_first_name(self):
        name = self.cleaned_data.get("recipient_first_name", "").strip()
        if not name:
            raise forms.ValidationError("نام گیرنده الزامی است.")
        return name