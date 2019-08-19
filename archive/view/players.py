from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render

from archive.models import Session, Player, User

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError

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
            # return HttpResponseRedirect('/archive/player/{0}'.format(player.pk))
            template_name = 'archive/player.html'
            context = {
                'message' : "player <{0}> successfully added".format(player.nickName),
                'player' : player
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save ({0})".format(e)
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
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
                # return HttpResponseRedirect('/archive/player/{0}'.format(player.pk))
                template_name = 'archive/player.html'
                context = {
                    'message' : "player <({0})> successfully modified".format(player.nickName),
                    'player' : player
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't modify player <{0}> because: ({1})".format(player.nickName,e)
                }
                # template = loader.get_template(template_name)
                # return HttpResponse(template.render(context, request))
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
            my_players=Player.objects.filter( owner_user = request.user.pk ).order_by('nickName')
            template_name = 'archive/players.html'
            context = {
                'message' : 'Player <{0}> successfully deleted'.format(nickName),
                'my_players' : my_players
            }
        except ProtectedError as e:
            template_name = 'archive/player.html'
            context = {
                'message' : "Couldn't delete player <{0}>, probably involved in at least one session ({1}).".format(nickName,e),
                'player' : player
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't delete ({0})".format(e)
            }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
