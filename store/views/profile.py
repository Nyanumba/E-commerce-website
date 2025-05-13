from django.shortcuts import render
from django.views import View
from store.models.order import Order
from store.models.customer import Customer

class Profile(View): 
    def get(self, request):
        customer_id = request.session.get('customer')
        if not customer_id:
            return render(request, 'profile.html', {'orders': [], 'error': 'Please log in to view your orders.'})

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return render(request, 'profile.html', {'orders': [], 'error': 'Customer not found.'})

        orders = Order.objects.filter(customer=customer).order_by('-date_ordered')
        return render(request, 'profile.html', {'orders': orders})