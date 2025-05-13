from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse
from store.models.product import Product
from store.models.order import Order
from store.models.customer import Customer
from store.models.report import ReportProduct, ReportOrder, OrderItem
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

class Checkout(View):
    """Handles the checkout process for Smart Computers"""

    def get(self, request):
        """Displays the checkout page with cart summary"""
        cart_key = f"cart_{request.session.get('customer', 'anonymous')}"
        cart = request.session.get(cart_key, {})
        if not cart:
            return redirect('cart')

        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(product.id): product for product in products}

        cart_items = []
        subtotal = 0
        out_of_stock_items = []

        for pid, qty in cart.items():
            product = product_dict.get(str(pid))
            if product:
                if product.quantity >= qty:
                    total = product.price * qty
                    subtotal += total
                    cart_items.append({
                        'product': product,
                        'quantity': qty,
                        'total': total
                    })
                else:
                    out_of_stock_items.append(product.name)

        if out_of_stock_items:
            error = f"Insufficient stock for: {', '.join(out_of_stock_items)}"
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'error': error
            })

        discount = subtotal * 0.05
        delivery_fee = 100
        total_price = subtotal - discount + delivery_fee

        # Fetch customer from session for display
        customer = None
        customer_id = request.session.get('customer')
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                del request.session['customer']
                return redirect('login')

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'discount': discount,
            'delivery_fee': delivery_fee,
            'total_price': total_price,
            'customer': customer
        })

    def post(self, request):
        """Processes the checkout and generates a receipt"""
        cart_key = f"cart_{request.session.get('customer', 'anonymous')}"
        cart = request.session.get(cart_key, {})
        if not cart:
            return redirect('cart')

        # Fetch cart items
        product_ids = [int(pid) for pid in cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(product.id): product for product in products}

        cart_items = []
        subtotal = 0
        out_of_stock_items = []

        for pid, qty in cart.items():
            product = product_dict.get(str(pid))
            if product:
                if product.quantity >= qty:
                    total = product.price * qty
                    subtotal += total
                    cart_items.append({
                        'product': product,
                        'quantity': qty,
                        'total': total
                    })
                else:
                    out_of_stock_items.append(product.name)

        if out_of_stock_items:
            error = f"Insufficient stock for: {', '.join(out_of_stock_items)}"
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'error': error
            })

        discount = subtotal * 0.05
        delivery_fee = 100
        total_price = subtotal - discount + delivery_fee

        # Fetch customer from session
        customer_id = request.session.get('customer')
        if not customer_id:
            return redirect('login')

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            del request.session['customer']
            return redirect('login')

        # Get form data
        destination = request.POST.get('destination')
        mpesa_number = request.POST.get('mpesa_number')

        if not destination or not mpesa_number:
            return render(request, 'checkout.html', {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'discount': discount,
                'delivery_fee': delivery_fee,
                'total_price': total_price,
                'customer': customer,
                'error': 'Please provide both destination and M-Pesa number.'
            })

        # Create ReportOrder for reporting
        report_order = ReportOrder.objects.create(
            customer=None,  # No User linked to Customer
            is_completed=True,
            total=total_price
        )
        logger.info(f"Created ReportOrder {report_order.id} with total {total_price}")

        # Save orders and reduce stock
        for item in cart_items:
            product = item['product']
            if product.reduce_stock(item['quantity']):
                # Create Order (existing logic)
                Order.objects.create(
                    customer=customer,
                    product=product,
                    quantity=item['quantity'],
                    price=item['total'],
                    address=destination,
                    phone=mpesa_number,
                    status='Pending'
                )
                # Create or get ReportProduct
                report_product, created = ReportProduct.objects.get_or_create(
                    name=product.name,
                    defaults={
                        'price': product.price,
                        'image': product.image if product.image else None,
                        'stock': product.quantity
                    }
                )
                if not created:
                    report_product.price = product.price
                    report_product.stock = product.quantity
                    report_product.save()
                # Create OrderItem for reporting
                OrderItem.objects.create(
                    order=report_order,
                    product=report_product,
                    quantity=item['quantity'],
                    price=product.price
                )
                logger.info(f"Created OrderItem for {product.name}, quantity {item['quantity']}")
            else:
                report_order.delete()
                return render(request, 'checkout.html', {
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                    'error': f"Stock update failed for {product.name}"
                })

        # Generate PDF receipt
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Company Name (Top-Left)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, 780, "Smart Computers")
        p.setFont("Helvetica", 10)
        p.drawString(50, 765, "Your Trusted Tech Store")

        # Receipt Header
        p.setFont("Helvetica-Bold", 12)
        p.drawString(250, 740, "Order Receipt")
        p.line(50, 735, 550, 735)

        # Receipt Details
        current_date = datetime.now().strftime("%B %d, %Y")
        customer_name = f"{customer.first_name} {customer.last_name}"
        phone_number = mpesa_number

        p.setFont("Helvetica", 11)
        p.drawString(50, 710, f"Date: {current_date}")
        p.drawString(50, 690, f"Customer: {customer_name}")
        p.drawString(50, 670, f"Destination: {destination}")
        p.drawString(50, 650, f"M-Pesa Number: {phone_number}")

        # Table Header for Order Details
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, 620, "Item")
        p.drawString(300, 620, "Qty")
        p.drawString(350, 620, "Price")
        p.drawString(450, 620, "Total")
        p.line(50, 615, 550, 615)

        # Table Content (Order Items)
        y = 595
        p.setFont("Helvetica", 11)
        for item in cart_items:
            p.drawString(50, y, item['product'].name[:30])
            p.drawString(300, y, str(item['quantity']))
            p.drawString(350, y, f"KES {item['product'].price:.2f}")
            p.drawString(450, y, f"KES {item['total']:.2f}")
            y -= 20
            if y < 100:
                p.showPage()
                p.setFont("Helvetica", 11)
                y = 780

        # Totals Section
        p.line(50, y, 550, y)
        y -= 20
        p.drawString(350, y, "Subtotal:")
        p.drawString(450, y, f"KES {subtotal:.2f}")
        y -= 20
        p.drawString(350, y, "Discount (5%):")
        p.drawString(450, y, f"-KES {discount:.2f}")
        y -= 20
        p.drawString(350, y, "Delivery Fee:")
        p.drawString(450, y, f"KES {delivery_fee:.2f}")
        y -= 20
        p.line(350, y, 550, y)
        y -= 20
        p.setFont("Helvetica-Bold", 11)
        p.drawString(350, y, "Total:")
        p.drawString(450, y, f"KES {total_price:.2f}")

        # Thank You Note
        y -= 40
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(50, y, "Thank you for shopping with Smart Computers, welcome again!")

        # Footer
        p.setFont("Helvetica", 9)
        p.drawString(50, 30, "Contact us: support@smartcomputers.com | +254 797 469 560")

        # Finalize PDF
        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="smart_computers_receipt.pdf"'

        # Clear the cart but preserve the session
        request.session[cart_key] = {}
        request.session.modified = True

        return response