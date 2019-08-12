from django.urls import path

from . import views

app_name = 'archive'
urlpatterns = [
    # ex: /archive/
    #path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('logout',views.logout_view,name='logout'),
    path('<int:Cycle_id>/',views.cycle_view,name='cycle'),
    path('session/<int:Session_id>/',views.session_view,name='session'),
    path("player", views.players_view,name='players'),
    path("player/<int:Player_id>", views.player_view,name='player'),
    path("scenario", views.scenarii_view,name='scenarii'),
    path("scenario/<int:Scenario_id>", views.scenario_view,name='scenario'),
    path("universe", views.universes_view,name='universes'),
    path("universe/<int:Universe_id>", views.universe_view,name='universe'),
]
