# RPG Session Archive Handling with Django
A little toy project to handle some python, django and DB.



## Files and dirs


### . directory
 * **db.sqlite3**: for a start we begin with a simple flat db, it is stored here


### rpgarchive directory
The project directory, holds most of the general settings

### archive directory
At least at the beginning of the development, the whole application will be considered a single django application named archive. Everything will then be dumped here.


## My django Odyssee step by step

### Basic stuff
tutorial https://docs.djangoproject.com/en/2.2/intro/tutorial01/
```bash
python -m django --version
#create a django project
django-admin startproject mysite
#launche a lightweight server on http://127.0.0.1:8000/
cd mysite; python manage.py runserver
# start the archive app in the current project
python manage.py startapp archive
```


### Creating Models
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



### Let's start to populate the DB
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
### Let's start to create views
#### First index view
First, in the archive/views.py we create the first view that will show all cycles for the connected user.
We make use of the `@login_required` class decorator to enforce connection.
We need to start and map urls in the application.
So, first we edit `rpgarchive/urls.py` and add `path('archive/', include('archive.urls'))` to the list.
Then, in `archive/urls.py` we can start and map archive urls to existing views
#### Refactoring the index view
We'll control the layout through a template file that we create in archive/templates/archive/index.html


We derive our class view from generic.ListView in order to benefit from the generic ListView
