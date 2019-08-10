from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.shortcuts import get_object_or_404, render

from django.urls import reverse
from django.views import generic
#from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Universe, Scenario, Author, Cycle, Session, Player


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'archive/index.html'
    context_object_name = 'my_list_of_cycles'

    def get_queryset(self):
        """Return all cycles that belong to the connected user
        """
        # return Cycle.objects.filter(owner_user = user.pk)
        return Cycle.objects.filter(owner_user = self.request.user.pk)
