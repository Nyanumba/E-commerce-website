from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from store.models.customer import Customer
from django.views import View

class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        postData = request.POST
        first_name, last_name, phone, email, password = (
            postData.get('firstname'),
            postData.get('lastname'),
            postData.get('phone'),
            postData.get('email'),
            postData.get('password')
        )

        error_message = None
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password=make_password(password)
        )

        if Customer.objects.filter(email=email).exists():
            error_message = 'Email Address Already Registered..'

        if not error_message:
            customer.save()  # Save the new user
            return redirect('login')  # Redirect to login after signup

        return render(request, 'signup.html', {'error': error_message})
