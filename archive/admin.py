from django.contrib import admin

# Register your models here.
from .models import Author, Universe, Scenario, Cycle, Session, Player
admin.site.register([Author, Universe, Scenario, Cycle, Session, Player])
