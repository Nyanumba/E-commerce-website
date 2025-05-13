from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from store.models.product import Product
from store.models.customer import Customer
from store.models.order import Order
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime

class Cart(View):
    """Handles displaying the cart"""
    
    def get(self, request):
        # Use session['customer'] for cart key
        cart_key = f"cart_{request.session.get('customer', 'anonymous')}"
        cart = request.session.get(cart_key, {})
        
        if not cart:
            return render(request, 'cart.html', {'cart_items': [], 'total_price': 0})

        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(product.id): product for product in products}

        cart_items = []
        total_price = 0

        for pid, qty in cart.items():
            product = product_dict.get(str(pid))
            if product:
                total = product.price * qty
                total_price += total
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'total': total
                })

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'total_price': total_price
        })

    def post(self, request):
        return redirect('cart')


class AddToCart(View):
    """Handles adding items to the cart"""
    
    def post(self, request):
        product_id = request.POST.get('product')
        if not product_id:
            return redirect('cart')

        product_id = str(product_id)
        cart_key = f"cart_{request.session.get('customer', 'anonymous')}"
        cart = request.session.get(cart_key, {})

        cart[product_id] = cart.get(product_id, 0) + 1
        request.session[cart_key] = cart
        request.session.modified = True

        return redirect('cart')


class DecreaseCartItem(View):
    """Handles decreasing product quantity"""

    def post(self, request):
        product_id = request.POST.get('product')
        if not product_id:
            return redirect('cart')

        product_id = str(product_id)
        cart_key = f"cart_{request.session.get('customer', 'anonymous')}"
        cart = request.session.get(cart_key, {})

        if product_id in cart:
            if cart[product_id] > 1:
                cart[product_id] -= 1
            else:
                del cart[product_id]
            request.session[cart_key] = cart
            request.session.modified = True

        return redirect('cart')


class RemoveFromCart(View):
    """Handles removing an item completely from the cart"""

    def post(self, request):
        product_id = request.POST.get('product')
        if not product_id:
            return redirect('cart')

        product_id = str(product_id)
        cart_key = f"cart_{request.session.get('customer', 'anonymous')}"
        cart = request.session.get(cart_key, {})

        if product_id in cart:
            del cart[product_id]
            request.session[cart_key] = cart
            request.session.modified = True

        return redirect('cart')



class ProductDisplay(View):
    #Handles displaying individual product details

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'productdisplay.html', {'product': product})