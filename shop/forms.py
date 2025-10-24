from django import forms
from .models import Product, Category, Brand, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "category", "brand", "description",
            "price", "sale_price", "currency",
            "stock", "thumbnail", "is_featured",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "category": forms.Select(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "brand": forms.Select(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "border rounded px-3 py-2 w-full"}),
            "price": forms.NumberInput(attrs={"step": "0.01", "class": "border rounded px-3 py-2 w-full"}),
            "sale_price": forms.NumberInput(attrs={"step": "0.01", "class": "border rounded px-3 py-2 w-full"}),
            "currency": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "stock": forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "thumbnail": forms.URLInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "mr-2"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["category"].queryset = Category.objects.order_by("name")
        self.fields["brand"].queryset = Brand.objects.order_by("name")
        self.fields["category"].empty_label = "Select a category"
        self.fields["brand"].empty_label = "Select a brand"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "content"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "class": "border rounded p-2 w-full"}),
            "title": forms.TextInput(attrs={"class": "border rounded p-2 w-full"}),
            "content": forms.Textarea(attrs={"rows": 3, "class": "border rounded p-2 w-full"}),
        }



class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "slug": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "parent"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "slug": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full"}),
            "parent": forms.Select(attrs={"class": "border rounded px-3 py-2 w-full"}),
        }