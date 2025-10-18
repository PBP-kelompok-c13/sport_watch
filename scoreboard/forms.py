from django import forms
from .models import scoreboard

class ScoreBoardForm(forms.ModelForm):
    class Meta:
        model = scoreboard
        fields = ['tim1', 'tim2', 'skor_tim1', 'skor_tim2']