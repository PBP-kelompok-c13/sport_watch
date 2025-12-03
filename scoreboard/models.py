from django.db import models
from django.utils import timezone

class Scoreboard(models.Model):
    SPORT_CHOICES = [
        ('NBA', 'NBA'),
        ('EPL', 'English Premier League'),
        ('NFL', 'NFL'),
        ('MLB', 'MLB'),
        ('NHL', 'NHL'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('recent', 'Recent'),
    ]

    tim1 = models.CharField(max_length=50)
    tim2 = models.CharField(max_length=50)
    skor_tim1 = models.IntegerField()
    skor_tim2 = models.IntegerField()
    logo_tim1 = models.URLField(blank=True, null=True)
    logo_tim2 = models.URLField(blank=True,  null=True)
    # buat admin
    tanggal = models.DateTimeField(default=timezone.now)
    sport = models.CharField(max_length=10, choices=SPORT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')

    def __str__(self):
        return f"{self.tim1} vs {self.tim2} ({self.sport}) - {self.status}"
