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
    template_name = 'archive/index.html'
    template = loader.get_template(template_name)
    my_list_of_cycles=Cycle.objects.filter(owner_user = request.user.pk)
    context = {
        'my_list_of_cycles' : my_list_of_cycles
    }
    return HttpResponse(template.render(context, request))
