from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from store.models.customer import Customer
from django.views import View

class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.objects.filter(email=email).first()
        error_message = 'Invalid email or password'

        if customer and check_password(password, customer.password):
            request.session['customer'] = customer.id
            return redirect('index')  # Redirect to index.html after login

        return render(request, 'login.html', {'error': error_message})

def logout(request):
    if 'customer' in request.session:
        del request.session['customer']  # Clear only customer ID, not entire session
    return redirect('login')