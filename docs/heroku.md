# My Heroku shity cheat sheet

## install
 * Install heroku’s command line interface (CLI) with `sudo snap install heroku --classic`
 * Connect to heroku server with `heroku login` (login schwarz.ben@gmail or schwarben) (I had to append a * to my usual shitty pwd)
 * Disconnect with `heroku logout`

## Requirements
Some files are needed at the root directory
 * **requirements.txt** (list of requirements, should at least contain `django` and most probably `gunicorn` which seems to be a lightweight wsgi interface to django, that is a lightweight webserver providing an interface with wsgi applications such as django apps. As for now I understan WSGI as a later child of the old CGI technology.).

 NB: When installing locally you can get the app's dependencies through `pip install -r requirements.txt`
 * **runtime.txt** (sets the python version for the app)
 * **Procfile** Apparently contains info concerning how the app should be run, what command to execute
```
web: gunicorn gettingstarted.wsgi --log-file -
```
Here, web means that the app should receive web traffic delegated to gunicorn

## Deployment and first minutes
 1. `heroku create` (shortcut for `heroku apps:create`): creates an app on the heroku server, prepares the system to receive my app (a default shitty name is provided pacific-citadel-39852) as well as a git remote (default name heroku). You can overide that name : `heroku apps:create rpgarchive`.
 1. `git push heroku master` Push on Heroku, normally a build follows.
 1. `heroku ps:scale web=1` Ensures that at least one instance of the app is running
 1. `heroku open` a shortcut to open the app in a browser. NB: it is also possible to lauch the app locally and get a browser access to it with `heroku local` or `heroku local web`
 1. `heroku logs --tail` check logs
 1. `heroku ps` check processus, load etc. Several instances of the app can be run at the same time; each is ran by a **dyno** (some lightweight container)
  * `heroku ps:scale web=0` scale the app to 0 process
  * `heroku ps:scale web=1` scale back to 1
 1. **Addons** (for instance, papertrail is some kind of logging, but apparently not free)
  * `heroku addons:create papertrail` add the addon ?
  * `heroku addons` check addons
  * `heroku addons:open papertrail` open it
 1. running commands on the server with `heroku run`
  * `heroku run python manage.py shell` runs the django shell on our app
  * `heroku run python manage.py collectstatic`
  * `heroku run ls`
 1. Environment variables
  * can be set in the `.env` file of the root directory
  * can be set on the fly
    * `heroku config:set TIMES=2`
    * `heroku config:unset TIMES`
  * check the environment with `heroku config`

## Database
 * `Heroku pg` more info on db
 * `heroku run python manage.py migrate`
 * `Heroku pg:psql` connects to the remote postgresql

## Some troubleshouting

### easy ones

 * Don't forget to add `ALLOWED_HOSTS = ["rpgarchive.herokuapp.com"]` in the global settings

### concerning statics

It seems static files are globally a hurdle in any framework.
As far as I understood, in django, `python manage.py collectstatic` gathers static files under a common directory. This is controlled by settings variables such as `STATIC_ROOT` (this is where all static files will be dumped by collectstatic) and `STATIC_DIRS` (where collectstatic should look for static files). Finally, `STATIC_URL` should be the url to map with the local directory undet `STATIC_ROOT`, but for some reasons this doesn't seem to work in production (`DEBUG=False`). Somehow it seems that the default more for django is to serve only dynamic files and bot static. I read several fix and warkaround proposals.


 * For some reason, you might experience troubles with the automatic collectstatic procedure after a `git push heroku master`. Someone advised to disable the procedure with `heroku config:set DISABLE_COLLECTSTATIC=1`. It is still necessary to run the colectstatic You could try to run a `heroku run python manage.py collectstatic --noinput` but I this seems to work only on a local dyno and does not impact the global environment. Therefore, someone advised to embed it in the `Profile` file :
 ```
 web: python my_django_app/manage.py collectstatic --noinput; bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT my_django_app/settings.py
 ```
 That appears a bit overkill to me though.

 * Ask django explicitely to (dynamically) serve the static files by adding
 ```
 re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
 ```
 to the app's urls. This doesn't seem to be the best solution, but as a temporary fix this is absolutely acceptable.

 * Apparently, people seem to use dedicated products for serving static files. Actually Heroku discourages people from serving static files from the heroku server which should be dedicated to the dynamic parts. Statics should thus be hosted somewhere else. That being said, it is still possible to host static files on Heroku. Many people seem to use third party software to deliver these files, and [Whitenoise](http://whitenoise.evans.io/en/stable/) seems to be a standard with the django/heroku/gunicorn combo.
   * Advice
`pip install WhiteNoise`
And change your `wsgi.py` file to this:
```
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
```
