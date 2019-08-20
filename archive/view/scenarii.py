from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render

from archive.models import Scenario, Universe, Author, User

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required

@login_required
def scenarii_view(request):
    my_scenarii=Scenario.objects.filter( owner_user = request.user.pk ).order_by("universe__name","title")
    template_name = 'archive/scenarii.html'
    context = {
        'my_scenarii' : my_scenarii
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

@login_required
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

@login_required
def scenario_add_view(request):
    """ This function is called on creation of a new Scenario
    It basically renders the scenario FORM and sets the form 'mode' to 'add' """
    form = modelform_factory(Scenario, fields=['title','comment','reference','universe','author'])
    return render(request,'archive/scenario-form.html',{'form':form, 'mode':'add'})
    

@login_required
def scenario_adding(request):
    """ This view is executed each time a user submits a new author for addition """
    # 'title','comment','reference','universe','author'

    form_title=request.POST['title'] #if request.POST['title'] != '' else None
    form_comment=request.POST['comment'] # blank=True, so should be a string anyway
    form_reference=request.POST['reference'] # blank=True, so should be a string anyway
    form_universe=request.POST['universe'] #if request.POST[''] != '' else None
    form_author=request.POST.getlist('author') #if request.POST[''] != '' else None
    # form_author=request.POST['author'] # only returns the last element from the list

    errors=[]
    if Scenario.objects.filter(owner_user = request.user.pk, title=form_title, universe=form_universe).exists() :
        errors.append( ('You already have a scenario by that name in the same universe',['name']) )

    if errors:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "\n".join( map( lambda x: x[0] , errors) )
        }
    else:
        try:
            scenario=Scenario(
                title=form_title,
                comment=form_comment,
                reference=form_reference,
                universe=Universe.objects.get(pk=form_universe),
                owner_user=request.user)
            scenario.save()
            scenario.author.add(*map(lambda x:Author.objects.get(pk=x),form_author))
            scenario.save()
            template_name = 'archive/scenario.html'
            context = {
                'message' : "scennario <{0}> successfully added".format(scenario.title),
                'scenario' : scenario
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save scenario <{0}> because: ({1})".format(form_title,e)
            }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

@login_required
def scenario_mod_view(request,Scenario_id):
    """ This function is called upon modification of an existing Scenario
    """
    scenario = Scenario.objects.get(pk=Scenario_id)
    if scenario.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this scenario is not yours)!"
            " <{0}!={1}>".format(scenario.owner_user.pk,request.user.pk)
        }
        template = loader.get_template(template_name)
        return HttpResponse(template.render(context, request))
    else :
        Form = modelform_factory(Scenario, fields=['title','comment','reference','universe','author'])
        form = Form(instance=scenario)
        return render(request,'archive/scenario-form.html',{'form':form, 'mode':'mod', 'scenario':scenario})

@login_required
def scenario_modifying(request,Scenario_id):
    scenario = Scenario.objects.get(pk = Scenario_id)
    if scenario.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this scenario is not yours)!"
            " <{0}!={1}>".format(scenario.owner_user.pk,request.user.pk)
        }
    else:
        form_title=request.POST['title'] #if request.POST['title'] != '' else None
        form_comment=request.POST['comment'] # blank=True, so should be a string anyway
        form_reference=request.POST['reference'] # blank=True, so should be a string anyway
        form_universe=request.POST['universe'] #if request.POST[''] != '' else None
        form_author=request.POST.getlist('author') #if request.POST[''] != '' else None
        # form_author=request.POST['author'] # only returns the last element from the list

        print ("Youpla title ({0}) - ({1}) --> {2}".format(form_title,scenario.title,form_title != scenario.title))
        print ("Youpla universe {0} - {1} --> {2}".format(form_universe,scenario.universe.pk,int(form_universe) != scenario.universe.pk))

        errors=[]
        if (form_title != scenario.title or int(form_universe) != scenario.universe.pk) and\
            Scenario.objects.filter(owner_user = request.user.pk, title=form_title, universe=form_universe).exists() :
            errors.append( ('You already have a scenario by that name in the same universe',['name']) )

        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
        else:
            scenario.title=form_title
            scenario.comment=form_comment
            scenario.reference=form_reference
            scenario.universe=Universe.objects.get(pk=form_universe)
            scenario.author.clear()
            scenario.author.add( *map(lambda x:Author.objects.get(pk=x),form_author) )

            try:
                scenario.save()
                template_name = 'archive/scenario.html'
                context = {
                    'message' : "scenario <({0})> successfully modified".format(scenario.title),
                    'scenario' : scenario
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't modify scenario <{0}> because: ({1})".format(scenario.title,e)
                }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


@login_required
def scenario_del_view(request,Scenario_id):
    """ """
    scenario = Scenario.objects.get(pk = Scenario_id)
    if scenario.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this scenario is not yours)!"
            " <{0}!={1}>".format(scenario.owner_user.pk,request.user.pk)
        }
    else:
        title=scenario.title
        try:
            scenario.delete()
            my_scenarii=Scenario.objects.filter( owner_user = request.user.pk ).order_by("universe__name","title")
            template_name = 'archive/scenarii.html'
            context = {
                'message' : 'Scenario <{0}> successfully deleted'.format(title),
                'my_scenarii' : my_scenarii
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't delete scenario ({0})".format(e)
            }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
