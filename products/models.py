from django.db import models

from django.utils.text import slugify
from django.contrib.auth.models import User


class ClientAdress(models.Model):
    client = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.TextField(max_length=2000, null=True, blank=True)
    tax_number = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    street_number = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=10)

    def __str__(self):
        return 'Adres klienta {}'.format(self.client.username)

    class Meta:
        verbose_name = 'Adres klienta'
        verbose_name_plural = 'Adresy klientów'


class Product(models.Model):
    name = models.CharField(null=False, max_length=255)
    producer = models.CharField(null=False, max_length=255)
    description = models.TextField()
    price = models.FloatField(max_length=3, null=False)
    image = models.ImageField(upload_to='media/images', null=False)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        name_and_producer = '{} {}'.format(self.producer, self.name)
        self.slug = slugify(name_and_producer)
        super(Product, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class OrderProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct, null=True)
    ordered = models.BooleanField(default=False)
    ordered_time = models.DateTimeField(blank=True, null=True)
    payment_time = models.DateTimeField(blank=True, null=True)
    value = models.FloatField(default=0)

    def __str__(self):
        return self.user.username
