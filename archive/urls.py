from django.urls import path

from . import views

app_name = 'archive'
urlpatterns = [
    # ex: /archive/
    #path('', views.index, name='index'),
    path('', views.IndexView.as_view(), name='index'),
    path('logout',views.logout_view,name='logout'),
    path('LetMeIn',views.letMeIn)
]
