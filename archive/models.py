from django.db import models
# import datetime
# from django.utils import timezone
from django.contrib.auth.models import User # User model is already provided by django

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=30)
    forename = models.CharField(max_length=30)
    email = models.EmailField(blank=False)
    ''' (Optional) this is allows to connect a player to another user of this application '''
    linked_user = models.ForeignKey(User, related_name='linked_player', null=True, on_delete=models.SET_NULL)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)


class Session(models.Model):
    timespan = models.DecimalField(max_digits=4, decimal_places=2,
        help_text="Champs décimal : entrez 4.5 pour quatre heure et demi de jeu.")
    date = models.DateTimeField()
    comments = models.TextField()
    nextSession = models.ForeignKey('self', on_delete=models.CASCADE)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    # This is where we connect our many to many to the Player table
    players = models.ManyToManyField(Player)

class Cycle(models.Model):
    NOT_YET_STARTED = "X--"; LABEL_NOT_YET_STARTED = "Pas commencé"
    RUNNING = "-->"; LABEL_RUNNING = "En cours"
    ABANDONED = " X "; LABEL_ABANDONED = "Abandonné"
    CLOSED = "--!"; LABEL_CLOSED = "Terminé"
    STATES = [ (NOT_YET_STARTED,LABEL_NOT_YET_STARTED), (RUNNING,LABEL_RUNNING),
        (ABANDONED,LABEL_ABANDONED), (CLOSED,LABEL_CLOSED) ]
    premiereSession = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    # RQ: used the class name 'Scenario' instead of the class itself because it is
    #     not yet defined here
    scenario = models.ForeignKey('Scenario',null=False,on_delete=models.PROTECT)
    codename = models.CharField(max_length=30,blank=False)
    comments = models.TextField()
    etat = models.CharField(max_length=3, choices=STATES, default=NOT_YET_STARTED)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)

# # relation ManyToMany joueur *participe à* session
# # NB: it seems django can handle that automatically with ManyToManyField field
# #     in any Model field definition
# class Participe(models.Model):
#     joueur = models.ForeignKey(joueur, on_delete=models.CASCADE)
#     session = models.ForeignKey(Session, on_delete=models.CASCADE)

"""Generic universe (Med fan, contemporary, ...) of specific games such as RdR, Elric, D&D..."""
class Universe(models.Model):
    name = models.CharField(max_length=30,blank=False)
    comment = models.TextField(blank=True)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)

class Scenario(models.Model):
    title = models.CharField(max_length=45,blank=False)
    """General comments about the scenario itself"""
    comment = models.TextField(blank=True,
        help_text="Commentaires généraux sur le scénario")
    """Where the scenario comes from, where can I find it"""
    reference = models.TextField(blank=True,
        help_text="Provenance du scénario, où peut-on le trouver")
    #document <-- At some point we might want to be able to store the documeent
    universe = models.ForeignKey(Universe,null=False, on_delete=models.PROTECT)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)

class Author(models.Model):
    name = models.CharField(max_length=30,blank=False)
    contact = models.TextField(blank=True,
        help_text="Comment peut-on contacter l'auteur ?")
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    #
    scenarios = models.ManyToManyField(Scenario)



# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')
#     # trying to attach a user to each question
#     user_owner = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.question_text
#
#     def was_published_recently(self):
#         now = timezone.now()
#         return now >= self.pub_date >= \
#             timezone.now() - datetime.timedelta(days=1)
#     # for use in the admin pannel
#     was_published_recently.admin_order_field = 'pub_date'
#     was_published_recently.boolean = True
#     was_published_recently.short_description = 'Published recently?'
