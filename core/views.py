from django.views import View
from django.shortcuts import render


class Index(View):
    def get(self, request):
        context = {} 
        return render(request, 'core/home.html', context)