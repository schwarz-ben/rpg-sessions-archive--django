from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render

from django.urls import reverse
from django.views import generic
#from django.utils import timezone

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Universe, Scenario, Author, Cycle, Session, Player


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



def players_view(request):
    my_players=Player.objects.filter( owner_user = request.user.pk )
    template_name = 'archive/players.html'
    context = {
        'my_players' : my_players
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

def player_view(request,Player_id):
    player=Player.objects.get( pk=Player_id )
    if player.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this player is not yours)!"
            " <{0}!={1}>".format(player.owner_user.pk,request.user.pk)
        }
    else:
        template_name = 'archive/player.html'
        context = {
            'player' : player
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))




def scenarii_view(request):
    my_scenarii=Scenario.objects.filter( owner_user = request.user.pk )
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





def authors_view(request):
    my_authors=Author.objects.filter( owner_user = request.user.pk )
    template_name = 'archive/authors.html'
    context = {
        'my_list_of_authors' : my_authors
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

def author_view(request,Author_id):
    author=Author.objects.get( pk=Author_id )
    if author.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this author is not yours)!"
            " <{0}!={1}>".format(author.owner_user.pk,request.user.pk)
        }
    else:
        template_name = 'archive/author.html'
        context = {
            'author' : author
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))






def universes_view(request):
    my_universes=Universe.objects.filter( owner_user = request.user.pk )
    template_name = 'archive/universes.html'
    context = {
        'my_universes' : my_universes
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

def universe_view(request,Universe_id):
    universe=Universe.objects.get( pk=Universe_id )
    if universe.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this universe is not yours)!"
            " <{0}!={1}>".format(universe.owner_user.pk,request.user.pk)
        }
    else:
        template_name = 'archive/universe.html'
        context = {
            'universe' : universe
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
