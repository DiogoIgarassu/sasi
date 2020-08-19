from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    #session = request.session
    #tempo_restante = session.get_expiry_age()
    '''key = request.COOKIES[settings.SESSION_COOKIE_NAME]
    print(key)
    request.session.set_expiry(1800)
    session = Session.objects.get(session_key=key)
    tempo_restante = session.expire_date
    tempo = datetime.time(tempo_restante)
    data = datetime.date(tempo_restante)'''

    return render(request, 'core/home.html')

def contact(request):
    return render(request, 'core/contact.html')


