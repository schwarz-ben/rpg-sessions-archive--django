from django.db import models
# import datetime
# from django.utils import timezone
from django.contrib.auth.models import User # User model is already provided by django

# Create your models here.

class Player(models.Model):
    nickName = models.CharField(max_length=30)
    name = models.CharField(max_length=30,null=True,blank=True)
    forename = models.CharField(max_length=30,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    ''' (Optional) this is allows to connect a player to another user of this application '''
    linked_user = models.ForeignKey(User, related_name='linked_player', null=True, blank=True,on_delete=models.SET_NULL)
    owner_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    def setNickName(self):
        if nickName is None:
            nickName = (name + " " + forename)[:29]

    def __str__(self):
        """Object string represention, is used in the admin field"""
        return self.nickName


class Session(models.Model):
    timespan = models.DecimalField(max_digits=4, decimal_places=2,
        help_text="Champs décimal : entrez 4.5 pour quatre heure et demi de jeu.")
    date = models.DateField()
    comments = models.TextField(null=True, blank=True)
    nextSession = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    owner_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    # This is where we connect our many to many to the Player table
    players = models.ManyToManyField(Player,through="M2M_Session_Players",related_name='sessions')
    # players = models.ManyToManyField(Player,db_table="M2M_Session_Player",related_name='sessions')


    def getPreviousSession(self):
        """returns the previous session, or None if there is none
        NB: there shouldn't be everal previous sessions, and the method should
        raise an error if this occurs"""
        qs=Session.objects.filter(nextSession=self.pk)
        if qs.exists():
            return qs.get()
        else:
            return None

    def getRelatedCycle(self):
        """ returns the cycle to which this session is attached, or None if none could be found
         Note that there SHOULD be one cycle, otherwise this should be considered a major bug"""
        s=self
        while s is not None:
            sp = s
            s = s.getPreviousSession()
        return Cycle.objects.filter(firstSession=sp.pk).get()

    def players_string(self):
        """ returns a coma separated list of nicknames for that session's players """
        return ", ".join( (p.nickName for p in self.players.all()) )

    def number_in_cycle(self):
        """ Returns the number of that session in the cycle.
        returns 1 for the first, 2 for the second etc...
        """
        c = self.getRelatedCycle()
        s = c.firstSession
        retVal= 1
        while s.pk != self.pk:
            s=s.nextSession
            retVal+=1
        return retVal

    def isLast(self):
        """Is this session the last session of the cycle

        returns True if this session is the last session of its cycle."""
        return self.nextSession is None

    def __str__(self):
        # return "<{0}-->{1}| '{2}' >".format(self.pk, "X" if self.nextSession is None else self.nextSession.pk, str(self.findRelatedCycle()))
        # return "<{0}>".format(self.pk)
        return "<{0}-->{1}>".format(self.pk, ("X" if self.nextSession is None else self.nextSession.pk) )

class M2M_Session_Players(models.Model):
     # session = models.ForeignKey('Session',null=False,blank=False,on_delete=models.PROTECT)
     session = models.ForeignKey('Session',null=False,blank=False,on_delete=models.CASCADE)
     player = models.ForeignKey('Player',null=False,blank=False,on_delete=models.PROTECT)



class Cycle(models.Model):
    NOT_YET_STARTED = "X--"; LABEL_NOT_YET_STARTED = "Pas commencé"
    RUNNING = "-->"; LABEL_RUNNING = "En cours"
    ABANDONED = " X "; LABEL_ABANDONED = "Abandonné"
    CLOSED = "--!"; LABEL_CLOSED = "Terminé"
    STATES = [ (NOT_YET_STARTED,LABEL_NOT_YET_STARTED), (RUNNING,LABEL_RUNNING),
        (ABANDONED,LABEL_ABANDONED), (CLOSED,LABEL_CLOSED) ]
    codename = models.CharField(max_length=30,blank=False)
    firstSession = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    # RQ: used the class name 'Scenario' instead of the class itself because it is
    #     not yet defined here
    scenario = models.ForeignKey('Scenario',null=False,on_delete=models.PROTECT)
    comments = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=3, choices=STATES, default=NOT_YET_STARTED)
    owner_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    def __str__(self):
        retVal = ""
        if self.codename is not None:
            retVal += self.codename
        if self.scenario.title is not None:
            retVal += " ("+self.scenario.title+")"
        return retVal

    def getRelatedSessions(self):
        '''returns the list of sessions attached to this cycle'''
        retList=[]
        s = self.firstSession
        while s is not None:
            retList.append(s)
            s=s.nextSession
        return retList

    def getLastSession(self):
        ''' returns the last session of this cycle

        if the cycle doesn't have a session, returns None '''
        s = self.firstSession
        prev=s
        while s is not None:
            prev=s
            s=s.nextSession
        return prev

    def gatherAllPlayers(self):
        """ returns the list of players that attented at least one session """
        raise NotImplemented()
        return []

    def gatherAllSessions(self):
        """ returns the list of sessions attached to this cycle

        Sessions are provided from the first (older one) to the last"""
        sl = []
        s = self.firstSession
        while s is not None:
            sl.append(s)
            s=s.nextSession
        return sl


# # relation ManyToMany joueur *participe à* session
# # NB: it seems django can handle that automatically with ManyToManyField field
# #     in any Model field definition
# class Participe(models.Model):
#     joueur = models.ForeignKey(joueur, on_delete=models.CASCADE)
#     session = models.ForeignKey(Session, on_delete=models.CASCADE)

"""Generic universe (Med fan, contemporary, ...) of specific games such as RdR, Elric, D&D..."""
class Universe(models.Model):
    name = models.CharField(max_length=30,blank=False,null=False)
    comment = models.TextField(blank=True,null=False,default='')
    owner_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Scenario(models.Model):
    title = models.CharField(max_length=45,blank=False,null=False)
    """General comments about the scenario itself"""
    comment = models.TextField(blank=True,
        help_text="Commentaires généraux sur le scénario")
    """Where the scenario comes from, where can I find it"""
    reference = models.TextField(blank=True,
        help_text="Provenance du scénario, où peut-on le trouver")
    #document <-- At some point we might want to be able to store the documeent
    universe = models.ForeignKey(Universe,null=False, on_delete=models.PROTECT)
    owner_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    #author = models.ForeignKey('Author',on_delete=models.SET_NULL)
    author = models.ManyToManyField('Author',through="M2M_Scenario_Author",related_name='authors')

    def author_names(self):
        """ returns the list of authors """
        return [a.name for a in self.author.all()]

    def authors_string(self):
        """ returns a comma separated list of all authors """
        return ", ".join( (a.name for a in self.author.all()) )

    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=30,blank=False)
    contact = models.TextField(blank=True,
        help_text="Comment peut-on contacter l'auteur ?")
    owner_user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    #
    # scenarios = models.ManyToManyField(Scenario)

    def __str__(self):
        return self.name

class M2M_Scenario_Author(models.Model):
    # I can delete a scenario, and by doing so I should delete all references to its authors
    scenario = models.ForeignKey('Scenario',null=False,blank=False,on_delete=models.CASCADE)
    # I cannot delete an author if I have a scenario from which he is an author
    author = models.ForeignKey('Author',null=False,blank=False,on_delete=models.PROTECT)


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
