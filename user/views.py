from django.urls import reverse_lazy
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.views.generic import FormView
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.models import AnonymousUser


class RegisterView(FormView):
    template_name = 'auth/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class BasePage(View):
    anonimys = AnonymousUser()

    def get(self, request):
        if request.user != self.anonimys:
           return redirect('dashboard')
        return redirect('login')
            