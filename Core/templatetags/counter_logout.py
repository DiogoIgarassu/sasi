from django.contrib.sessions.models import Session
from django.conf import settings
from django import template
from django.template import RequestContext


register = template.Library()

@register.inclusion_tag('core/templatetags/counter_logout.html')
def counter_logout():


    key = request.COOKIES[settings.SESSION_COOKIE_NAME]
    request.session.set_expiry(1800)
    session = Session.objects.get(session_key=key)
    tempo_restante = session.expire_date

    context = {'ob': tempo_restante}

    return context