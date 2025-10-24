from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Berita, KategoriBerita, Comment

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline',
            'placeholder': '******************'
        })

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'
            })

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none',
                'rows': 3,
                'placeholder': 'Join the discussion and leave a comment!'
            }),
        }


class KategoriBeritaForm(forms.ModelForm):
    """
    A form for creating and updating KategoriBerita instances.
    """
    class Meta:
        model = KategoriBerita
        fields = ['nama'] # Users will typically only need to edit the name.
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'Enter category name'}),
        }

class BeritaForm(forms.ModelForm):
    """
    A form for creating and updating Berita instances.
    """
    class Meta:
        model = Berita
        fields = [
            'judul',
            'konten',
            'kategori',
            'thumbnail',
            'sumber',
            'penulis',
            'is_published'
        ]

        widgets = {
            'judul': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'Enter the article title'}),
            'konten': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'rows': 10}),
            'kategori': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'thumbnail': forms.URLInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'https://example.com/image.jpg'}),
            'sumber': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'placeholder': 'e.g., Detik Sport, ESPN'}),
            'penulis': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        }