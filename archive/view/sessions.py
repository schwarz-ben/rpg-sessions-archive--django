from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404

from archive.models import Cycle,Session,User,Player

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required



@login_required
def sessions_view(request):
    sessions=Session.objects.filter( owner_user = request.user.pk ).order_by('-date')
    template_name = 'archive/sessions.html'
    context = {
        'my_sessions' : sessions
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


@login_required
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



@login_required
def session_mod_view(request,Session_id):
    """ This function is called upon modification of an existing session
    """
    session = Session.objects.get(pk=Session_id)
    if session.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this session is not yours)!"
            " <{0}!={1}>".format(session.owner_user.pk,request.user.pk)
        }
        template = loader.get_template(template_name)
        return HttpResponse(template.render(context, request))
    else :
        Form = modelform_factory(Session, fields=['timespan','date','comments','players'])
        form = Form(instance=session)
        return render(request,'archive/session-form.html',{'form':form, 'mode':'mod', 'session':session})

@login_required
def session_modifying(request,Session_id):
    session = Session.objects.get(pk = Session_id)
    if session.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this session is not yours)!"
            " <{0}!={1}>".format(session.owner_user.pk,request.user.pk)
        }
    else:
        Form = modelform_factory(Session, fields=['timespan','date','comments','players'])
        form = Form(initial=request.POST)

        form_timespan=request.POST['timespan']
        form_date=request.POST['date']
        form_comments=request.POST['comments']
        form_players=request.POST.getlist('players')

        errors=[]
        if not form.is_valid() :
            for field,message in form.errors:
                errors.append( (field,"Error on field {0}: ({1})".format(message,[field])) )
        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }

        else:
            session.timespan=form_timespan
            session.date=form_date
            session.comment=form_comments
            session.players.set(form_players)

            try:
                session.save()
                template_name = 'archive/session.html'
                context = {
                    'message' : "cycle <({0})> successfully modified".format(session),
                    'session' : session
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't modify session <{0}> because: ({1})".format(session,e)
                }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))







@login_required
def session_add_view(request,Session_id):
    """ This function is called on creation of a new Session when a previous session exists

    It basically renders the cycle FORM and sets the form 'mode' to 'add' """
    form = modelform_factory(Session, fields=['timespan','date','comments','players'])
    return render(request,'archive/session-form.html',{'form':form, 'mode':'add', 'Session_id':Session_id})



@login_required
def session_adding(request,Session_id):
    """ This view is executed each time a user submits a new session form for addition """
    session = Session.objects.get(pk = Session_id)
    if session.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this session is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        Form = modelform_factory(Session, fields=['timespan','date','comments','players'])
        form = Form(initial=request.POST)

        form_timespan=request.POST['timespan']
        form_date=request.POST['date']
        form_comments=request.POST['comments']
        form_players=request.POST.getlist('players')

        errors=[]
        if not form.is_valid() :
            for field,message in form.errors:
                errors.append( (field,"Error on field {0}: ({1})".format(message,[field])) )
        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        else:
            try:
                new_session=Session.objects.create(timespan=form_timespan,date=form_date,comments=form_comments,owner_user=request.user)
                new_session.save()
                try:
                    new_session.players.add(*map(lambda x:Player.objects.get(pk=x),form_players))
                    next_session=session.nextSession
                    new_session.nextSession=next_session
                    new_session.save()
                    session.nextSession = new_session
                    session.save()
                except :
                    new_session.delete()
                    session.nextSession = next_session
                    session.save()
                    raise
                template_name = 'archive/session.html'
                context = {
                    'message' : "Session successfully added",
                    'session' : session
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't add session because: ({1})".format(e)
                    }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))




@login_required
def session_del_view(request,Session_id):
    """ Supress a given session"""
    session = Session.objects.get(pk = Session_id)
    if session.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this session is not yours)!"
            " <{0}!={1}>".format(session.owner_user.pk,request.user.pk)
        }
    elif not session.isLast():
        template_name = 'archive/error.html'
        context = {
            'error_message' : "Can't remove this session, it is not the last in its cycle !"
        }
    else:
        try:
            session.delete()
            my_sessions=Session.objects.filter( owner_user = request.user.pk )
            template_name = 'archive/sessions.html'
            context = {
                'message' : 'Session <{0}> successfully deleted',
                'my_sessions' : my_sessions
            }
        # except ProtectedError as e:
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't delete ({0})".format(e)
            }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
