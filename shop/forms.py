from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "content"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min":1, "max":5, "class":"border rounded p-2 w-20"}),
            "title": forms.TextInput(attrs={"class":"border rounded p-2 w-full"}),
            "content": forms.Textarea(attrs={"rows":3, "class":"border rounded p-2 w-full"}),
        }
