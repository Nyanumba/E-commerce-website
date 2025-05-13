from django.shortcuts import render
from django.views import View

class Homepage(View):
    def get(self, request):
        return render(request, 'homepage.html')