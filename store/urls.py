from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views.homepage import Homepage
from .views.index import Index
from .views.profile import Profile
from .views.cart import Cart, AddToCart, DecreaseCartItem, RemoveFromCart, ProductDisplay
from. views.checkout import  Checkout
from .views.report import SalesReportView

from .views.signup import Signup
from .views.contacts import Contact
from .views.login import Login, logout
from store.views.report import SalesReportView, SalesReportPDFView


urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('signup/', Signup.as_view(), name='signup'),
    path('cart/', Cart.as_view(), name='cart'),
    path('cart/add/', AddToCart.as_view(), name='add_to_cart'),
    path('cart/decrease/', DecreaseCartItem.as_view(), name='decrease_cart_item'),
    path('cart/remove/', RemoveFromCart.as_view(), name='remove_from_cart'),
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('contacts/', Contact.as_view(), name='contacts'), 
    path('index/', Index.as_view(), name='index'),
    path('product/<int:product_id>/', ProductDisplay.as_view(), name='product_display'),
    path('profile/', Profile.as_view(), name='profile'),
    path('reports/', SalesReportView.as_view(), name='sales_report'),
    path('reports/pdf/', SalesReportPDFView.as_view(), name='sales_report_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT[0])
