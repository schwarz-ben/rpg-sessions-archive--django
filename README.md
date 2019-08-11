# RPG Session Archive Handling with Django
A little toy project to handle some python, django and DB.

## Files and dirs
### . directory
 * **db.sqlite3**: for a start we begin with a simple flat db, it is stored here
### rpgarchive directory
The project directory, holds most of the general settings
### archive directory
At least at the beginning of the development, the whole application will be considered a single django application named archive. Everything will then be dumped here.

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

## Links
 * A [Journal](docs/journal.md) of my django odyssee
 * Django [links](links.md) of interrest
