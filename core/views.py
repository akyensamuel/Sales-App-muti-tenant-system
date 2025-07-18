from django.contrib.auth import logout
from django.shortcuts import redirect
def logout_to_home(request):
    logout(request)
    return redirect('home')
from django.views import View
from django.shortcuts import render


class Index(View):
    def get(self, request):
        context = {} 
        return render(request, 'core/home.html', context)