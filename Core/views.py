from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def home(request):
    return render(request, 'core/home.html')

def contact(request):
    return render(request, 'core/contact.html')


