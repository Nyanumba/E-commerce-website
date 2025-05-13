from django.shortcuts import render
from django.views import View
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from store.models.report import ReportOrder, ReportProduct, OrderItem
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import io
import logging

# Set up logging
logger = logging.getLogger(__name__)

class SalesReportView(View):
    def get(self, request):
        # Fetch all completed orders
        orders = ReportOrder.objects.filter(is_completed=True)
        logger.info(f"Found {orders.count()} completed orders")

        # Log customer associations
        customer_orders = orders.values('customer__email').annotate(total=Sum('total'))
        logger.info(f"Customer order breakdown: {list(customer_orders)}")

        # Calculate metrics
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        total_orders = orders.count()

        # Top products by quantity sold
        top_products = OrderItem.objects.filter(
            order__is_completed=True,
            product__isnull=False
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('price') * F('quantity'), output_field=DecimalField())
        ).order_by('-total_quantity')[:5]
        logger.info(f"Top products: {list(top_products)}")

        context = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'top_products': top_products,
            'start_date': 'All Time',
            'end_date': timezone.now().date(),
        }
        logger.debug(f"Context: {context}")

        return render(request, 'sales_report.html', context)

class SalesReportPDFView(View):
    def get(self, request):
        # Fetch all completed orders
        orders = ReportOrder.objects.filter(is_completed=True)
        total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        total_orders = orders.count()
        top_products = OrderItem.objects.filter(
            order__is_completed=True,
            product__isnull=False
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('price') * F('quantity'), output_field=DecimalField())
        ).order_by('-total_quantity')[:5]

        # Create PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Smart Computers")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, "Sales Report")
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 90, f"Period: All Time to {timezone.now().date()}")
        p.line(50, height - 100, width - 50, height - 100)

        # Overview
        y = height - 130
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Overview")
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(50, y, f"Total Revenue: KES {total_revenue:.2f}")
        y -= 20
        p.drawString(50, y, f"Total Orders: {total_orders}")
        if total_orders == 0:
            y -= 20
            p.setFillColor(colors.red)
            p.drawString(50, y, "No completed sales recorded.")
            p.setFillColor(colors.black)
        y -= 30

        # Top Products Table
        if top_products:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Top Products")
            y -= 20

            # Table data
            data = [["Product", "Quantity Sold", "Revenue (KES)"]]
            for product in top_products:
                data.append([
                    product['product__name'][:30],  # Truncate long names
                    str(product['total_quantity']),
                    f"{product['total_revenue']:.2f}"
                ])

            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            # Draw table
            table_width = width - 100
            table.wrapOn(p, table_width, 400)
            table.drawOn(p, 50, y - len(data) * 20)
            y -= (len(data) * 20 + 20)
        else:
            p.setFont("Helvetica", 11)
            p.setFillColor(colors.red)
            p.drawString(50, y, "No products sold.")
            p.setFillColor(colors.black)

        # Footer
        p.setFont("Helvetica", 9)
        p.drawString(50, 30, "Smart Computers | support@smartcomputers.com | +254 797 469 560")

        # Finalize PDF
        p.showPage()
        p.save()
        buffer.seek(0)

        # Return PDF response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="smart_computers_sales_report.pdf"'
        logger.info("Generated sales report PDF")
        return response