from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render,get_object_or_404

from archive.models import Cycle,Session,Scenario,User,Player

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required

@login_required
def cycles_view(request):
    my_cycles=Cycle.objects.filter( owner_user = request.user.pk )
    template_name = 'archive/cycles.html'
    context = {
        'my_cycles' : my_cycles
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

@login_required
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

@login_required
def cycle_add_view(request):
    """ This function is called on creation of a new Cycle
    It basically renders the cycle FORM and sets the form 'mode' to 'add' """
    form = modelform_factory(Cycle, fields=['codename','scenario','comments','state'])
    return render(request,'archive/cycle-form.html',{'form':form, 'mode':'add'})


# fields=['codename','firstSession','scenario','comments','state']


        # codename
        # firstSession
        # scenario
        # comments
        # state
        # owner_user



@login_required
def cycle_adding(request):
    """ This view is executed each time a user submits a new cycle for addition """
    # 'title','comment','reference','universe','author'
    form_codename=request.POST['codename']
    # form_firstSession=request.POST['firstSession']
    form_scenario=request.POST['scenario']
    form_comments=request.POST['comments']
    form_state=request.POST['state']


    Form = modelform_factory(Cycle, fields=['codename','scenario','comments','state'])
    form = Form(initial=request.POST)
    errors=[]
    if not form.is_valid() :
        for field,message in form.errors:
            errors.append( (field,"Error on field {0}: ({1})".format(message,[field])) )
    if Cycle.objects.filter(owner_user = request.user.pk, codename=form_codename).exists() :
        errors.append( ('You already have a cycle with that name',['codename']) )
    if errors:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "\n".join( map( lambda x: x[0] , errors) )
        }
    else:
        try:
            cycle=Cycle(
                codename=form_codename,
                # firstSession=form_firstSession,
                scenario=Scenario.objects.get(pk=form_scenario),
                comments=form_comments,
                state=form_state,
                owner_user=request.user)
            cycle.save()
            template_name = 'archive/cycle.html'
            context = {
                'message' : "cycle <{0}> successfully added".format(cycle.codename),
                'cycle' : cycle
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save cycle <{0}> because: ({1})".format(form_codename,e)
            }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

@login_required
def cycle_mod_view(request,Cycle_id):
    """ This function is called upon modification of an existing cycle
    """
    cycle = Cycle.objects.get(pk=Cycle_id)
    if cycle.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
        template = loader.get_template(template_name)
        return HttpResponse(template.render(context, request))
    else :
        # Form = modelform_factory(Cycle, fields=['codename','firstSession','scenario','comments','state'])
        Form = modelform_factory(Cycle, fields=['codename','scenario','comments','state'])
        form = Form(instance=cycle)
        return render(request,'archive/cycle-form.html',{'form':form, 'mode':'mod', 'cycle':cycle})


@login_required
def cycle_modifying(request,Cycle_id):
    cycle = Cycle.objects.get(pk = Cycle_id)
    if cycle.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        form_codename=request.POST['codename']
        # form_firstSession=request.POST['firstSession']
        form_scenario=request.POST['scenario']
        form_comments=request.POST['comments']
        form_state=request.POST['state']

        Form = modelform_factory(Cycle, fields=['codename','scenario','comments','state'])
        form = Form(initial=request.POST)
        errors=[]
        if not form.is_valid() :
            for field,message in form.errors:
                errors.append( (field,"Error on field {0}: ({1})".format(message,[field])) )

        if (form_codename != cycle.codename) and Cycle.objects.filter(owner_user = request.user.pk, codename=form_codename).exists() :
            errors.append( ('You already have a cycle with that name',['codename']) )

        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        else:
            cycle.codenamme=form_codename
            # form_firstSession
            cycle.scenario=Scenario.objects.get(pk=form_scenario)
            cycle.comments=form_comments
            cycle.state=form_state

            try:
                cycle.save()
                template_name = 'archive/cycle.html'
                context = {
                    'message' : "cycle <({0})> successfully modified".format(cycle.codename),
                    'cycle' : cycle
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't modify cycle <{0}> because: ({1})".format(cycle.codename,e)
                }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


@login_required
def cycle_del_view(request,Cycle_id):
    """ """
    cycle = Cycle.objects.get(pk = Cycle_id)
    if cycle.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        codename=cycle.codename
        try:
            for s in reversed(cycle.gatherAllSessions()):
                s.delete()
            cycle.delete()
            my_cycles=Cycle.objects.filter( owner_user = request.user.pk ).order_by('codename')
            template_name = 'archive/cycles.html'
            context = {
                'message' : 'Cycle <{0}> successfully deleted'.format(codename),
                'my_cycles' : my_cycles
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't delete cycle ({0})".format(e)
            }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))



@login_required
def add_session(request,Cycle_id):
    """ add a session to an exhisting cycle
    if the cycle doesn't have a session yet, it will be created

    if the cycle already has a session, we'll create a last session for the cycle """

    cycle = Cycle.objects.get(pk = Cycle_id)
    if cycle.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        if cycle.firstSession is not None :
            s = cycle.getLastSession()
            return HttpResponseRedirect("/archive/session-add/{0}".format(s.pk))
        else:
            # form = modelform_factory(Session, fields=['timespan','date','comments','nextSession','players'])
            form = modelform_factory(Session, fields=['timespan','date','comments','players'])
            return render(request,'archive/session-form.html',{'form':form, 'mode':'first', 'Cycle_id':Cycle_id})

def do_add_session(request,Cycle_id):
    """ add the first session to a cycle """
    cycle = Cycle.objects.get(pk = Cycle_id)
    if cycle.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this cycle is not yours)!"
            " <{0}!={1}>".format(cycle.owner_user.pk,request.user.pk)
        }
    else:
        # form = modelform_factory(Session, fields=['timespan','date','comments','nextSession','players'])
        Form = modelform_factory(Session, fields=['timespan','date','comments','players'])
        form = Form(initial=request.POST)

        form_timespan=request.POST['timespan']
        form_date=request.POST['date']
        form_comments=request.POST['comments']
        #nextSession=request.POST['']
        form_players=request.POST.getlist('players')

        errors=[]
        if not form.is_valid() :
            for field,message in form.errors:
                errors.append( (field,"Error on field {0}: ({1})".format(message,[field])) )
        if cycle.firstSession is not None :
            errors.append( ('Cannot attach a first session to this cycle ({0}), it already has one'.format(cycle.codename),['firstSession']) )

        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        else:
            try:
                session=Session.objects.create(timespan=form_timespan,date=form_date,comments=form_comments,owner_user=request.user)
                session.save()
                try:
                    session.players.add(*map(lambda x:Player.objects.get(pk=x),form_players))
                    session.save()
                    cycle.firstSession = session
                    cycle.save()
                except :
                    session.delete()
                    raise
                template_name = 'archive/cycle.html'
                context = {
                    'message' : "First session successfully added to cycle <{0}>".format(cycle.codename),
                    'cycle' : cycle
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't add session to cycle <{0}> because: ({1})".format(cycle.codename,e)
                    }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

    # timespan
    # date
    # comments
    # nextSession
    # players
