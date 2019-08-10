from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render

from django.urls import reverse
from django.views import generic
#from django.utils import timezone

from django.contrib.auth.decorators import login_required

from .models import Universe, Scenario, Author, Cycle, Session, Player

#
#   DEFAULT FIRST VIEW
@login_required
def index(request):
    lines=["Hello {0}, here are your ongoing games:".format(request.user.username),"<ul>"]
    ql=Cycle.objects.filter(owner_user = request.user.pk)
    for c in ql:
        lines.append("<li><a href='cycle/{0}'>{1}</a></li>".format(c.pk,c.codename))
    lines.append("</ul>")

    return HttpResponse("\n".join(lines))
