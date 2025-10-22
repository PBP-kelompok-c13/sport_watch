from django import forms
from .models import Berita, KategoriBerita, Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
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
        # The slug should be generated automatically in the view.

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
            'judul': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the article title'}),
            'konten': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'kategori': forms.Select(attrs={'class': 'form-select'}),
            'thumbnail': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
            'sumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Detik Sport, ESPN'}),
            'penulis': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the category dropdown start with a placeholder.
        self.fields['kategori'].empty_label = "Select a Category"
        # Make the author dropdown optional if it's not required.
        self.fields['penulis'].empty_label = "Select an Author"