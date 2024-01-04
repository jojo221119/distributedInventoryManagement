from django.db import models

class MeinModell(models.Model):
    titel = models.CharField(max_length=100)
    inhalt = models.TextField()
    erstelldatum = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'warehouse'

    def __str__(self):
        return self.titel
