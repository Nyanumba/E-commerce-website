from django.db import models
from .category import Category

class Product(models.Model):  # Changed to singular 'Product'
    name = models.CharField(max_length=60)
    brand = models.CharField(max_length=60, default='', blank=True, null=True)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/products/')
    quantity = models.PositiveIntegerField(default=0, help_text="Number of units in stock")  # New field

    def __str__(self):
        return self.name

    def reduce_stock(self, amount):
        """Reduce stock by the given amount if sufficient quantity exists."""
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
            return True
        return False

    @staticmethod
    def get_products_by_id(ids):
        products = Product.objects.filter(id__in=ids)
        return products  # Simplified; removed dict conversion as it seems incomplete in original

    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def get_all_products_by_categoryid(category_id):
        return Product.objects.filter(category=category_id) if category_id else Product.get_all_products()