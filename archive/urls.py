from django.urls import path


from archive import view
from archive.view import views,players,universes,authors,scenarii

app_name = 'archive'
urlpatterns = [
    # ex: /archive/
    #path('', views.index, name='index'),
    path('logout',view.views.logout_view,name='logout'),

    path('', view.views.IndexView.as_view(), name='index'),
    path('<int:Cycle_id>/',view.views.cycle_view,name='cycle'),

    path("sessions", view.views.sessions_view,name='sessions'),
    path('session/<int:Session_id>/',view.views.session_view,name='session'),

    path("player", view.players.players_view,name='players'),
    path("player/<int:Player_id>", view.players.player_view,name='player'),
    path("player-add/",view.players.player_form_view,name='player-add'),
    path("player-do-add/",view.players.player_adding,name='player-adding'),
    path("player-mod/<int:Player_id>",view.players.player_mod_view,name='player-mod'),
    path("player-del/<int:Player_id>",view.players.player_del_view,name='player-del'),
    path("player-do-modify/<int:Player_id>",view.players.player_modifying,name='player-modifying'),

    path("scenario", view.scenarii.scenarii_view,name='scenarii'),
    path("scenario/<int:Scenario_id>", view.scenarii.scenario_view,name='scenario'),
    path("scenario-add/",view.scenarii.scenario_add_view,name='scenario-add'),
    path("scenario-do-add/",view.scenarii.scenario_adding,name='scenario-adding'),
    path("scenario-mod/<int:Scenario_id>",view.scenarii.scenario_mod_view,name='scenario-mod'),
    path("scenario-del/<int:Scenario_id>",view.scenarii.scenario_del_view,name='scenario-del'),
    path("scenario-do-modify/<int:Scenario_id>",view.scenarii.scenario_modifying,name='scenario-modifying'),

    path("authors", view.authors.authors_view,name='authors'),
    path("author/<int:Author_id>", view.authors.author_view,name='author'),
    path("author-add/",view.authors.author_add_view,name='author-add'),
    path("author-do-add/",view.authors.author_adding,name='author-adding'),
    path("author-mod/<int:Author_id>",view.authors.author_mod_view,name='author-mod'),
    path("author-del/<int:Author_id>",view.authors.author_del_view,name='author-del'),
    path("author-do-modify/<int:Author_id>",view.authors.author_modifying,name='author-modifying'),

    path("universe", view.universes.universes_view,name='universes'),
    path("universe/<int:Universe_id>", view.universes.universe_view,name='universe'),
    path("universe-add/",view.universes.universe_form_view,name='universe-add'),
    path("universe-do-add/",view.universes.universe_adding,name='universe-adding'),
    path("universe-mod/<int:Universe_id>",view.universes.universe_mod_view,name='universe-mod'),
    path("universe-del/<int:Universe_id>",view.universes.universe_del_view,name='universe-del'),
    path("universe-do-modify/<int:Universe_id>",view.universes.universe_modifying,name='universe-modifying'),
]
