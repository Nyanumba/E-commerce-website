from django.db import models
from .product import Product
from .customer import Customer

class Order(models.Model):
    """Represents a customer order for a product in Smart Computers."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, help_text="The customer placing the order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, help_text="The product being ordered")
    date_ordered = models.DateTimeField(auto_now_add=True, help_text="Date the order was placed")
    price = models.IntegerField(help_text="Total price for this order (quantity * product price)")
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Shipped', 'Shipped'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled')
        ],
        default='Pending',
        help_text="Current status of the order"
    )
    address = models.CharField(max_length=100, default='', blank=True, help_text="Delivery address")
    phone = models.CharField(max_length=20, default='', blank=True, help_text="Contact phone number")
    quantity = models.PositiveIntegerField(default=1, help_text="Number of units ordered")

    def __str__(self):
        return f"{self.product.name} - {self.customer.first_name} {self.customer.last_name}"

    def save(self, *args, **kwargs):
        """Override save to ensure price reflects quantity * product.price if not set."""
        if not self.price:  # Only set if price isn’t manually provided
            self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-date_ordered']  # Newest first