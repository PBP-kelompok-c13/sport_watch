from django.db import models

class scoreboard(models.Model):
    tim1 = models.CharField(max_length=50)
    tim2 = models.CharField(max_length=50)
    skor_tim1 = models.IntegerField()
    skor_tim2 = models.IntegerField()
    tanggal = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.tim1} vs {self.tim2}"
