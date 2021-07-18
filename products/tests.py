from django.test import TestCase
from .models import ClientAdress, Product, OrderProduct, Order
from django.core.files.uploadedfile import SimpleUploadedFile
from .tests_utils import delete_test_image
from django.contrib.auth.models import User

# models tests


PRODUCT_DATA = {'name': 'Test item name',
                'producer': 'Test item producer',
                'description': 'Test item description',
                'price': 3.25,
                'image': SimpleUploadedFile(name='test_image.jpg',
                                            content=open('media/images/test_image.jpg', 'rb').read(),
                                            content_type='image/jpeg'),

                }

ORDER_DATA = {'quantity': 2, 'ordered': False}


class ClientAdressTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = User.objects.create(username='test_user')
        company = 'test company'
        tax_number = 23
        name = 'test name'
        surname = 'test surname'
        street = 'test street'
        zip_code = 'test zip code'
        city = 'test city'
        street_number = 'test street number'
        apartment_number = 'test apartment number'
        ClientAdress.objects.create(client=cls.client, company=company, tax_number=tax_number, name=name,
                                    surname=surname, street=street, zip_code=zip_code, city=city,
                                    street_number=street_number, apartment_number=apartment_number)

    def test_client_adress_pass(self):
        record = ClientAdress.objects.get(name='test name')
        self.assertTrue(isinstance(record, ClientAdress))
        self.assertTrue(isinstance(record.client, User))

    def test_client_adress_fail(self):
        record = ClientAdress.objects.get(name='test name')
        self.assertFalse(record.client.username == 'tester')


class ProductTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name=PRODUCT_DATA['name'], producer=PRODUCT_DATA['producer'], description=PRODUCT_DATA['description'],
            price=PRODUCT_DATA['price'], image=PRODUCT_DATA['image'])

    def tearDown(self):
        delete_test_image()

    def test_product_pass(self):
        record = Product.objects.get(name='Test item name')  # self.product?
        self.assertTrue(isinstance(record, Product))
        self.assertEqual(record.__str__(), record.name)

    def test_product_fail(self):
        record = Product.objects.get(name='Test item name')
        self.assertFalse(isinstance(record, User))


class OrderProductTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = User.objects.create(username='test_user')
        cls.product = Product.objects.create(
            name=PRODUCT_DATA['name'], producer=PRODUCT_DATA['producer'], description=PRODUCT_DATA['description'],
            price=PRODUCT_DATA['price'], image=PRODUCT_DATA['image'])
        quantity = 2
        ordered = False
        cls.order_product = OrderProduct.objects.create(
            user=cls.client, product=cls.product, quantity=quantity, ordered=ordered)

    def tearDown(self):
        delete_test_image()

    def test_product_pass(self):
        self.assertTrue(isinstance(self.order_product, OrderProduct))
        self.assertEqual(self.order_product.ordered, False)

    def test_product_fail(self):
        self.assertFalse(self.order_product.quantity > 5)


class OrderTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = User.objects.create(username='test_user')
        cls.product = Product.objects.create(
            name=PRODUCT_DATA['name'], producer=PRODUCT_DATA['producer'], description=PRODUCT_DATA['description'],
            price=PRODUCT_DATA['price'], image=PRODUCT_DATA['image'])
        cls.order_product = [OrderProduct.objects.create(user=cls.client, product=cls.product,
                                                        quantity=ORDER_DATA['quantity'], ordered=ORDER_DATA['ordered'])]
        cls.order = Order.objects.create(user=cls.client, value=1000)
        cls.order.products.set(cls.order_product)

    def tearDown(self):
        delete_test_image()

    def test_order_pass(self):
        self.assertTrue(isinstance(self.order, Order))
        self.assertEqual(self.order.value, 1000)

    def test_order_fail(self):
        self.assertFalse(isinstance(self.order.user, Order))


# views tests

