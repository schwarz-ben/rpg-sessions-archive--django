from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render

from django.urls import reverse
from django.views import generic
#from django.utils import timezone

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Universe, Scenario, Author, Cycle, Session, Player, User

from django.forms import modelform_factory



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
# #     PLAYERS
# #
# ##############################

def players_view(request):
    my_players=Player.objects.filter( owner_user = request.user.pk ).order_by('nickName')
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

def player_form_view(request):
    playerForm = modelform_factory(Player, fields=['nickName', 'name', 'forename','email', 'linked_user'])
    return render(request,'archive/player-form.html',{'form':playerForm, 'mode':'add'})

def player_mod_view(request,Player_id):
    player = Player.objects.get(pk=Player_id)
    if player.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this player is not yours)!"
            " <{0}!={1}>".format(player.owner_user.pk,request.user.pk)
        }
        template = loader.get_template(template_name)
        return HttpResponse(template.render(context, request))
    else :
        PlayerForm = modelform_factory(Player, fields=['nickName', 'name', 'forename','email', 'linked_user'])
        playerForm = PlayerForm(instance=player)
        return render(request,'archive/player-form.html',{'form':playerForm, 'mode':'mod', 'player':player})

def player_adding(request):
    """ This view is executed each time a usr submits a new player for addition """
    his_nickName=request.POST['nickName']
    his_name=request.POST['name'] if request.POST['name'] != '' else None
    his_forename=request.POST['forename'] if request.POST['forename'] else None
    his_email=request.POST['email'] if request.POST['email'] else None
    his_linked_user=User.objects.get(pk=request.POST['linked_user']) if request.POST['linked_user'] else None
    errors=[]
    if Player.objects.filter(owner_user = request.user.pk, nickName=his_nickName).exists() :
        errors.append( ('You already have a player with that nickname',['nickName']) )
    if (his_name or his_forename) and Player.objects.filter(owner_user = request.user.pk, name=his_name, forename=his_forename).exists() :
        errors.append( ('You already have a player both with that name and forename',['name','forename']) )

    if errors:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "\n".join( map( lambda x: x[0] , errors) )
        }
        # template = loader.get_template(template_name)
        # return HttpResponse(template.render(context, request))
    else:
        try:
            player=Player(nickName=his_nickName,
                     name=his_name,
                     forename=his_forename,
                     email=his_email,
                     linked_user=his_linked_user,
                     owner_user=request.user)
            player.save()
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save ({0})".format(e)
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        # return HttpResponseRedirect('/archive/player/{0}'.format(player.pk))

        template_name = 'archive/player.html'
        context = {
            'message' : "player <{0}> successfully added".format(player.nickName),
            'player' : player
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


def player_modifying(request,Player_id):
    player = Player.objects.get(pk = Player_id)
    if player.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this player is not yours)!"
            " <{0}!={1}>".format(player.owner_user.pk,request.user.pk)
        }
    else:
        form_nickName=request.POST['nickName']
        form_name=request.POST['name'] if request.POST['name'] != '' else None
        form_forename=request.POST['forename'] if request.POST['forename'] else None
        form_email=request.POST['email'] if request.POST['email'] else None
        form_linked_user=User.objects.get(pk=request.POST['linked_user']) if request.POST['linked_user'] else None

        errors=[]

        if (form_nickName != player.nickName) and Player.objects.filter(owner_user = request.user.pk, nickName=form_nickName).exists() :
            errors.append( ('You already have a player with that nickname',['nickName']) )
        if (form_name != player.name or form_forename != player.forename) and Player.objects.filter(owner_user = request.user.pk, name=form_name, forename=form_forename).exists() :
            errors.append( ('You already have a player both with that name and forename',['name','forename']) )


        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        else:
            if form_nickName != player.nickName : player.nickName = form_nickName
            if form_name != player.name : player.name = form_name
            if form_forename != player.forename : player.forename = form_forename
            if form_email != player.email : player.email = form_email
            if form_linked_user != player.linked_user : player.linked_user = form_linked_user

            try:
                player.save()
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't save ({0})".format(e)
                }
                # template = loader.get_template(template_name)
                # return HttpResponse(template.render(context, request))

            # return HttpResponseRedirect('/archive/player/{0}'.format(player.pk))
            template_name = 'archive/player.html'
            context = {
                'message' : "player <({0})> successfully modified".format(player.nickName),
                'player' : player
            }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))



def player_del_view(request,Player_id):
    """ """
    player = Player.objects.get(pk = Player_id)
    if player.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this player is not yours)!"
            " <{0}!={1}>".format(player.owner_user.pk,request.user.pk)
        }
    else:
        nickName=player.nickName
        try:
            player.delete()
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save ({0})".format(e)
            }
        my_players=Player.objects.filter( owner_user = request.user.pk ).order_by('nickName')
        template_name = 'archive/players.html'
        context = {
            'message' : 'Player <{0}> successfully deleted'.format(nickName),
            'my_players' : my_players
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

# ##############################
# #
# #     AUTHORS
# #
# ##############################

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

# ##############################
# #
# #     UNIVERSE
# #
# ##############################

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
