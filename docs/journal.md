
# My django Odyssee step by step

## setting github access through ssh on my local repo
First, I copied my `rsa.pub` file onto the github dedicated page (somewhere under 'my account' --> 'settings' --> 'security' ).
Then I tested the connection:
```
# This worked
ssh -T git@github.com
# This didn't work, hence it seemed impossible to connect to my accoun through ssh
ssh -vT schwarz-ben@github.com
# but actually, for sad stories like mine, the github staff thought of a hook:
git remote set-url origin git@github.com:schwarz-ben/rpg-sessions-archive--django.git
# just check it was registered
git remote get-url origin
# And all works fine now
```
## Basic stuff
```bash
python -m django --version
#create a django project
django-admin startproject mysite
#launche a lightweight server on http://127.0.0.1:8000/
cd mysite; python manage.py runserver
# start the archive app in the current project
python manage.py startapp archive
```


## Creating Models
Models are the database objects, they are written under archive/models.py.
Once this is done, we tell django to create the tables that correspond to these models.
Actually, django Models also contain links to related Models (through ForeignKeys and ManyToManyFields),
which allows for easy navigations without bothering with SQL queries.

```bash
# models have been changed in the app and we request changes to be stored as a migration
# (files on disk with data related objects, models, SQL commands etc)
python manage.py makemigrations archive
# shows the SQL commands that will be issued by the migration, and store them somewhere under archive/migration
python manage.py sqlmigrate archive 0001
# (optionally) checks for possible problems that would be raised by a migration
python manage.py check
# Performs the actual migration
python manage.py migrate
```

Some errors encountered :

```
schwarz@sansa:~/sandbox/django/rpgarchive$ ./manage.py makemigrations archive/
No installed app with label 'archive/'.
```
Simply forgot to register the archive app in the global project.
Just edited rpgarchive/rpgarchive/settings.py and added
`'archive.apps.ArchiveConfig'` at the beginning of the `INSTALLED_APPS` list.

```
archive.Player.linked_user: (fields.E304) Reverse accessor for 'Player.linked_user' clashes with reverse accessor for 'Player.owner_user'.
	HINT: Add or change a related_name argument to the definition for 'Player.linked_user' or 'Player.owner_user'.
```

ForeignKey create circular links. Even if the field is defined from model A to model B,
there is also a link created from B towards A. For this reason, when two ForeignKeys are defined from A to B,
there is an ambiguity on the way back.
Therefore, it is necessary to explicitely name at least one of the two links, such as here in the `Player` Model
```python
  linked_user = models.ForeignKey(User, related_name='linked_player', null=True, on_delete=models.SET_NULL)
  owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
```


## Let's start to populate the DB
```bash
# let's create a superuser
python manage.py createsuperuser
# and let's run the surver and access the admin webpage
./manage.py runserver
firefox http://127.0.0.1:8000/admin/
```
In order to allow access to the models in the admin pannel, edit archive/admin and add
```python
from .models import Author, Universe, Scenario, Cycle, Session, Player
admin.site.register([Author, Universe, Scenario, Cycle, Session, Player])
```
Starting from there, it is possible to start and fill up the DB through the admin pannel.
The DB can also be filled and interrogated from a shell session
```bash
python manage.py shell
>>> from archive.models import Cycle
>>> Cycle.objects.filter(codename__startswith="Old")
<QuerySet [<Cycle: Oldies like cake too>]>
>>> Cycle.objects.filter(codename__contains="Old")
<QuerySet [<Cycle: Oldies like cake too>]>
Cycle.objects.filter(scenario__title__contains="Yverssaire")
```

## Let's start to create views
### First index view
First, in the archive/views.py we create the first view that will show all cycles for the connected user.
We make use of the `@login_required` class decorator to enforce connection.
We need to start and map urls in the application.
So, first we edit `rpgarchive/urls.py` and add `path('archive/', include('archive.urls'))` to the list.
Then, in `archive/urls.py` we can start and map archive urls to existing views
### Refactoring the index view to use templates and css
In order to better separate the controler and the view (MVC style), we extract as much view related stuff from the view.py file (the namme is somehow missleading, in the end we'd like the view.py file to be essentiially the controler.).
We'll control the layout through a template file that we create in `archive/templates/archive/index.html`
and some css file in `archive/static/archive`.
### Refactoring the index view to make use of generic views
Most of the modifications take place in `models.py` where the index view function has been replaced by a class derived from a view.
The `url.py` file is also impacted: we don't call a function anymore, but we call `the as_view()` method of the class.
Note that `@login_required` is not available on classes, and to enforce login (since django 1.9) we can derive from `LoginRequiredMixin`; another possibility is to insert the template call in a `login_required( ... )` in the `url.py` file.

## Let's fool around with templates
 * `{% block name %}` allows to define block area in a parent template, say parent.html
 * Another template can then derive from this template, suffice to start with `{% extends "parent.html" %}`
 * In this child template one can fillup the blocks `{% block name %}` that were defined in the parent

## Let's polish all this login/logout stuff
It turns out I was able to play around on my webstite because I started with some connection on the admin page, and that this page redirected me on some login process.
After that, I was automatically session based connected.
Now I inserted a logout button that disconnected me, and this is the good moment to investigate this whole login/logout process.
We won't deal with this ourselves, and instead we'll use the Models, protocols and whatever template that django provides as a default.

As a default, django installs the auth app that handles authentication (cf `settings` in `INSTALLED_APPS`).

We then should make sure we give access to the authentication pages.
For instance adding
`path('accounts/', include('django.contrib.auth.urls'))`
in the project `url.py`.

Default views are also provided in the `auth` package, which we will use, but we'll need to write templates.
When it comes to login, as a default django looks for a `login.html` template in a global `Templates/registration` directory.

it is then necessary to add this new path `os.path.join(BASE_DIR, 'templates')` to the `TEMPLATE.DIR` field of the global `settings` file.

Finally in the same `RPGArchive/settings.py` file we can set `LOGIN_REDIRECT_URL=/archive` to automatically redirect the user to this page upon correct login.

## Dumping here a few technical gore elements
### User authentication and permissions
#### In the code

for view fonctions
```python
@login_required
@permission_required('polls.can_vote', raise_exception=True)
def my_view(request):
```
With Class based views
```python
from django.contrib.auth.mixins import UserPassesTestMixin
def my_view(request):
    if not request.user.is_authenticated:
class MyView(UserPassesTestMixin, View):
```

#### In template files
```
@permission_required('polls.can_vote', login_url='/loginpage/')
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}. Thanks for logging in.</p>
{% if perms.foo %}
{% if perms.foo.can_vote %}
```
