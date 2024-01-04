from django.shortcuts import render
from .models import MeinModell

def startseite(request):
    eintraege = MeinModell.objects.all()
    return render(request, 'startseite.html', {'eintraege': eintraege})
