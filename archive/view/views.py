from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render

from django.urls import reverse
from django.views import generic
#from django.utils import timezone

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from archive.models import Universe, Scenario, Author, Cycle, Session, Player, User

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError

# ##############################
# #
# #     CYCLE
# #
# ##############################

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'archive/index.html'
    context_object_name = 'my_list_of_cycles'

    def get_queryset(self):
        """Return all cycles that belong to the connected user
        """
        # return Cycle.objects.filter(owner_user = user.pk)
        return Cycle.objects.filter(owner_user = self.request.user.pk)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/archive")

def cycle_view(request,Cycle_id):
    # retrieving the cycle or redirect to a 404 page
    cycle = get_object_or_404(Cycle, pk=Cycle_id)
    if cycle.owner_user.pk != request.user.pk:
        # print ("{0}!={1}".format(cycle.owner_user,request.user.pk))
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        template_name = 'archive/cycle.html'
        context = {
            'cycle' : cycle,
            'my_session_list' : cycle.getRelatedSessions()
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

# ##############################
# #
# #     SESSIONS
# #
# ##############################

def sessions_view(request):
    sessions=Session.objects.filter( owner_user = request.user.pk ).order_by('-date')
    template_name = 'archive/sessions.html'
    context = {
        'my_list_of_sessions' : sessions
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))



def session_view(request,Session_id):
    session = get_object_or_404(Session, pk=Session_id)
    if session.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        template_name = 'archive/session.html'
        context = {
            'session' : session
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


# ##############################
# #
# #     SCENARIO
# #
# ##############################

def scenarii_view(request):
    my_scenarii=Scenario.objects.filter( owner_user = request.user.pk ).order_by("universe__name","title")
    template_name = 'archive/scenarii.html'
    context = {
        'my_scenarii' : my_scenarii
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

def scenario_view(request,Scenario_id):
    scenario=Scenario.objects.get( pk=Scenario_id )
    if scenario.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this scenario is not yours)!"
            " <{0}!={1}>".format(scenario.owner_user.pk,request.user.pk)
        }
    else:
        template_name = 'archive/scenario.html'
        context = {
            'scenario' : scenario
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
