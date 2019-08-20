from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render

from archive.models import Author, User

from django.forms import modelform_factory

from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required

@login_required
def authors_view(request):
    """ Renders the list of all authors for the connected user """
    my_authors=Author.objects.filter( owner_user = request.user.pk )
    template_name = 'archive/authors.html'
    context = {
        'my_authors' : my_authors
        }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

@login_required
def author_view(request,Author_id):
    """ The detailed view for an author """
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


@login_required
def author_add_view(request):
    """ This function is called on creation of a new Author
    It basically renders the author FORM and sets the form 'mode' to 'add' """
    form = modelform_factory(Author, fields=['name','contact'])
    return render(request,'archive/author-form.html',{'form':form, 'mode':'add'})

@login_required
def author_mod_view(request,Author_id):
    """ This function is called upon modification of an existing author
    """
    author = Author.objects.get(pk=Author_id)
    if author.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this author is not yours)!"
            " <{0}!={1}>".format(author.owner_user.pk,request.user.pk)
        }
        template = loader.get_template(template_name)
        return HttpResponse(template.render(context, request))
    else :
        Form = modelform_factory(Author, fields=['name', 'contact'])
        form = Form(instance=author)
        return render(request,'archive/author-form.html',{'form':form, 'mode':'mod', 'author':author})

@login_required
def author_adding(request):
    """ This view is executed each time a user submits a new author for addition """
    form_name=request.POST['name'] if request.POST['name'] != '' else None
    form_contact=request.POST['contact'] if request.POST['contact'] else ""

    errors=[]
    if Author.objects.filter(owner_user = request.user.pk, name=form_name).exists() :
        errors.append( ('You already have an author with that name',['name']) )

    if errors:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "\n".join( map( lambda x: x[0] , errors) )
        }
    else:
        try:
            author=Author(name=form_name,
                     contact=form_contact,
                     owner_user=request.user)
            author.save()
            template_name = 'archive/author.html'
            context = {
                'message' : "author <{0}> successfully added".format(author.name),
                'author' : author
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't save author <{0}> because: ({1})".format(form_name,e)
            }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))

@login_required
def author_modifying(request,Author_id):
    author = Author.objects.get(pk = Author_id)
    if author.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this author is not yours)!"
            " <{0}!={1}>".format(author.owner_user.pk,request.user.pk)
        }
    else:
        form_name=request.POST['name'] if request.POST['name'] != '' else None
        form_contact=request.POST['contact'] if request.POST['contact'] else None
        errors=[]

        if (form_name != author.name) and Author.objects.filter(owner_user = request.user.pk, name=form_name).exists() :
            errors.append( ('You already have an Author with that name',['name']) )


        if errors:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "\n".join( map( lambda x: x[0] , errors) )
            }
            # template = loader.get_template(template_name)
            # return HttpResponse(template.render(context, request))
        else:
            if form_name != author.name : author.name = form_name
            if form_contact != author.contact : author.contact = form_contact

            try:
                author.save()
                template_name = 'archive/author.html'
                context = {
                    'message' : "author <({0})> successfully modified".format(author.name),
                    'author' : author
                }
            except Exception as e:
                template_name = 'archive/error.html'
                context = {
                    'error_message' : "couldn't modify author <{0}> because: ({1})".format(author.name,e)
                }
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


@login_required
def author_del_view(request,Author_id):
    """ """
    author = Author.objects.get(pk = Author_id)
    if author.owner_user.pk != request.user.pk:
        template_name = 'archive/error.html'
        context = {
            'error_message' : "You are not supposed to access this page (this author is not yours)!"
            " <{0}!={1}>".format(author.owner_user.pk,request.user.pk)
        }
    else:
        name=author.name
        try:
            author.delete()
            my_authors=Author.objects.filter( owner_user = request.user.pk ).order_by('name')
            template_name = 'archive/authors.html'
            context = {
                'message' : 'Author <{0}> successfully deleted'.format(name),
                'my_authors' : my_authors
            }
        except Exception as e:
            template_name = 'archive/error.html'
            context = {
                'error_message' : "couldn't delete author ({0})".format(e)
            }

    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))
