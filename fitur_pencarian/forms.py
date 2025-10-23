from django import forms
from portal_berita.models import KategoriBerita
from shop.models import Category, Brand

from .models import SearchPreference


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        label="Kata kunci",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Cari berita, produk, atau kata kunci lain...",
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            }
        ),
    )
    search_in = forms.ChoiceField(
        choices=SearchPreference.SearchScope.choices,
        initial=SearchPreference.SearchScope.ALL,
        label="Cari di",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            }
        ),
    )
    news_category = forms.ModelChoiceField(
        queryset=KategoriBerita.objects.none(),
        required=False,
        label="Kategori Berita",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            }
        ),
    )
    product_category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Kategori Produk",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            }
        ),
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.none(),
        required=False,
        label="Brand",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
            }
        ),
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=12,
        decimal_places=2,
        label="Harga Minimum",
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "0",
            }
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=12,
        decimal_places=2,
        label="Harga Maksimum",
        widget=forms.NumberInput(
            attrs={
                "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                "placeholder": "1.000.000",
            }
        ),
    )
    only_discount = forms.BooleanField(
        required=False,
        label="Hanya tampilkan diskon",
        widget=forms.CheckboxInput(
            attrs={
                "class": "rounded border-gray-300 text-blue-600 focus:ring-blue-500",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["news_category"].queryset = KategoriBerita.objects.order_by("nama")
        self.fields["product_category"].queryset = Category.objects.order_by("name")
        self.fields["brand"].queryset = Brand.objects.order_by("name")

    def clean(self):
        cleaned = super().clean()
        min_price = cleaned.get("min_price")
        max_price = cleaned.get("max_price")
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(
                "Harga minimum tidak boleh lebih besar dari harga maksimum."
            )
        return cleaned


class SearchPreferenceForm(forms.ModelForm):
    class Meta:
        model = SearchPreference
        fields = [
            "label",
            "description",
            "default_scope",
            "default_news_category",
            "default_product_category",
            "default_brand",
            "min_price",
            "max_price",
            "only_discount",
            "is_public",
            "role_visibility",
        ]
        widgets = {
            "label": forms.TextInput(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                    "placeholder": "Contoh: Diskon Sepak Bola",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                    "placeholder": "Catatan singkat mengenai preset ini",
                }
            ),
            "default_scope": forms.Select(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                }
            ),
            "default_news_category": forms.Select(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                }
            ),
            "default_product_category": forms.Select(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                }
            ),
            "default_brand": forms.Select(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                }
            ),
            "min_price": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                    "placeholder": "0",
                }
            ),
            "max_price": forms.NumberInput(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                    "placeholder": "1.000.000",
                }
            ),
            "only_discount": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 focus:ring-blue-500",
                }
            ),
            "is_public": forms.CheckboxInput(
                attrs={
                    "class": "rounded border-gray-300 text-blue-600 focus:ring-blue-500",
                }
            ),
            "role_visibility": forms.Select(
                attrs={
                    "class": "w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.request_user = user
        super().__init__(*args, **kwargs)
        self.fields["default_news_category"].queryset = KategoriBerita.objects.order_by(
            "nama"
        )
        self.fields["default_product_category"].queryset = Category.objects.order_by(
            "name"
        )
        self.fields["default_brand"].queryset = Brand.objects.order_by("name")
        if not (user and user.is_staff):
            # non staff tidak boleh membuat preset khusus staf
            self.fields["role_visibility"].choices = [
                (
                    SearchPreference.RoleVisibility.ALL.value,
                    SearchPreference.RoleVisibility.ALL.label,
                )
            ]
            self.fields["role_visibility"].initial = (
                SearchPreference.RoleVisibility.ALL.value
            )
        else:
            self.fields["role_visibility"].choices = SearchPreference.RoleVisibility.choices

    def clean(self):
        cleaned = super().clean()
        min_price = cleaned.get("min_price")
        max_price = cleaned.get("max_price")
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(
                "Harga minimum tidak boleh lebih besar dari harga maksimum."
            )
        role_visibility = cleaned.get("role_visibility")
        if role_visibility == SearchPreference.RoleVisibility.STAFF and not (
            self.request_user and self.request_user.is_staff
        ):
            raise forms.ValidationError(
                "Anda tidak memiliki izin untuk membuat preset khusus staf."
            )
        return cleaned
