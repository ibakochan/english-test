from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy('main:profile')