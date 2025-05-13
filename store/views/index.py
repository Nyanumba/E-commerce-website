from django.shortcuts import render, redirect, HttpResponseRedirect
from store.models.product import Product
from store.models.category import Category
from django.views import View

class Index(View):

    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})

        if cart.get(product):
            if remove:
                if cart[product] <= 1:
                    cart.pop(product)
                else:
                    cart[product] -= 1
            else:
                cart[product] += 1
        else:
            cart[product] = 1

        request.session['cart'] = cart
        return redirect('homepage')

    def get(self, request):
        categories = Category.get_all_categories()
        categoryID = request.GET.get('category')
        products = Product.get_all_products_by_categoryid(categoryID) if categoryID else Product.get_all_products()
        return render(request, 'index.html', {'products': products, 'categories': categories})
