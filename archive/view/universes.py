from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render

from archive.models import Universe, User

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError




def universes_view(request):

    """ Renders the complete list of universes for a registered user """

    my_universes=Universe.objects.filter( owner_user = request.user.pk )
    template_name = 'archive/universes.html'
    context = {
        'my_universes' : my_universes
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))




def universe_view(request,Universe_id):

    """ Renders the detailed view of a given universe """

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


def universe_form_view(request):
    """ This function is called on creation of a new Universe
    It basically renders the universe FORM and sets the form 'mode' to 'add' """
    form = modelform_factory(Universe, fields=['name','comment'])
    return render(request,'archive/universe-form.html',{'form':form, 'mode':'add'})


def universe_mod_view(request,Universe_id):
    """ This function is colled upon modification of an existing Universe
    """
    universe = Universe.objects.get(pk=Universe_id)
    if universe.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this universe is not yours)!"
            " <{0}!={1}>".format(universe.owner_user.pk,request.user.pk)
        }
        template = loader.get_template(template_name)
        return HttpResponse(template.render(context, request))
    else :
        Form = modelform_factory(Universe, fields=['name', 'comment'])
        form = Form(instance=universe)
        return render(request,'archive/universe-form.html',{'form':form, 'mode':'mod', 'universe':universe})

def universe_adding(request):
    """ This view is executed each time a user submits a new univrese for addition """
    form_name=request.POST['name'] if request.POST['name'] != '' else None
    form_comment=request.POST['comment'] if request.POST['comment'] else ""

    errors=[]
    if Universe.objects.filter(owner_user = request.user.pk, name=form_name).exists() :
        errors.append( ('You already have a universe with that name',['name']) )

    if errors:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "\n".join( map( lambda x: x[0] , errors) )
        }
    else:
        try:
            universe=Universe(name=form_name,
                     comment=form_comment,
                     owner_user=request.user)
            universe.save()
            template_name = 'archive/universe.html'
            context = {
                'message' : "universe <{0}> successfully added".format(universe.name),
                'universe' : universe
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save universe <{0}> because: ({1})".format(universe.name,e)
            }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


def universe_modifying(request,Universe_id):
    universe = Universe.objects.get(pk = Universe_id)
    if universe.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this universe is not yours)!"
            " <{0}!={1}>".format(universe.owner_user.pk,request.user.pk)
        }
    else:
        form_name=request.POST['name'] if request.POST['name'] != '' else None
        form_comment=request.POST['comment'] if request.POST['comment'] else ""
        errors=[]

        if (form_name != universe.name) and Universe.objects.filter(owner_user = request.user.pk, name=form_name).exists() :
            errors.append( ('You already have a universe with that name',['name']) )


        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        else:
            if form_name != universe.name : universe.name = form_name
            if form_comment != universe.comment : universe.comment = form_comment

            try:
                universe.save()
                # return HttpResponseRedirect('/archive/player/{0}'.format(player.pk))
                template_name = 'archive/universe.html'
                context = {
                    'message' : "universe <({0})> successfully modified".format(universe.name),
                    'universe' : universe
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't modify universe <{0}> because: ({1})".format(universe.name,e)
                }
                # template = loader.get_template(template_name)
                # return HttpResponse(template.render(context, request))
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))



def universe_del_view(request,Universe_id):
    """ """
    universe = Universe.objects.get(pk = Universe_id)
    if universe.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this universe is not yours)!"
            " <{0}!={1}>".format(universe.owner_user.pk,request.user.pk)
        }
    else:
        name=universe.name
        try:
            universe.delete()
            my_universes=Universe.objects.filter( owner_user = request.user.pk ).order_by('name')
            template_name = 'archive/universes.html'
            context = {
                'message' : 'Universe <{0}> successfully deleted'.format(name),
                'my_universes' : my_universes
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't delete ({0})".format(e)
            }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
