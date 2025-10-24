from django import forms
from .models import Scoreboard

class ScoreBoardForm(forms.ModelForm):
    class Meta:
        model = Scoreboard
        fields = ['tim1', 'tim2', 'skor_tim1', 'skor_tim2', 'sport', 'status', 'tanggal', 'logo_tim1', 'logo_tim2']
        widgets = {
            'sport': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 px-3 py-2 text-sm text-gray-700'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-lg border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 px-3 py-2 text-sm text-gray-700'
            }),
            'tanggal': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'w-full rounded-lg border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 px-3 py-2 text-sm text-gray-700'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'logo_tim1': forms.URLInput(attrs={
                'placeholder': 'https://example.com/logo-team1.png',
                'class': 'w-full rounded-lg border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 px-3 py-2 text-sm text-gray-700'
            }),
            'logo_tim2': forms.URLInput(attrs={
                'placeholder': 'https://example.com/logo-team2.png',
                'class': 'w-full rounded-lg border border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 px-3 py-2 text-sm text-gray-700'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tanggal'].input_formats = ['%Y-%m-%dT%H:%M']
