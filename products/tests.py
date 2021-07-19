from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .models import ClientAdress, Product, OrderProduct, Order
from .tests_utils import delete_test_image


# models tests
def create_user():
    return User.objects.create(username='test_user')


def create_product():
    name = 'Test item name'
    producer = 'Test item producer'
    description = 'Test item description'
    price = 3.25
    image = SimpleUploadedFile(name='test_image.jpg', content=open('media/images/test_image.jpg', 'rb').read(),
                                content_type='image/jpeg')
    return Product.objects.create(name=name, producer=producer, description=description, price=price, image=image)


def create_order_product(user, product):
    return OrderProduct.objects.create(user=user, product=product, quantity=2, ordered=False)


def create_order():
    pass


class ClientAdressTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = create_user()
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
        cls.product = create_product()

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
        cls.client = create_user()
        cls.product = create_product()
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
        cls.client = create_user()
        cls.product = create_product()
        cls.order_product = create_order_product(cls.client, cls.product)
        cls.order = Order.objects.create(user=cls.client, value=1000)
        cls.order.products.set([cls.order_product])

    def tearDown(self):
        delete_test_image()

    def test_order_pass(self):
        self.assertTrue(isinstance(self.order, Order))
        self.assertEqual(self.order.value, 1000)

    def test_order_fail(self):
        self.assertFalse(isinstance(self.order.user, Order))


# views tests


class LoginViewTest(TestCase):

    def test_login_page_pass(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_logging_in_user(self):
        c = Client()
        user = create_user()
        user.set_password('test')
        user.save()
        response = c.post(reverse('log_in'), {'username': 'test_user', 'password': 'test'})
        user = get_user(c)
        self.assertEqual(user.username, 'test_user')
        self.assertFalse(user.is_anonymous)
        response = c.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_fail(self):
        response = self.client.get(reverse('log_in'))
        self.assertNotIn('auth.user', response.context)


class LogoutViewTest(TestCase):

    def test_logout_page_pass(self):
        response = self.client.get(reverse('log_out'))
        self.assertRedirects(response, expected_url='/products/log_in?next=/products/log_out/',
                             status_code=302, target_status_code=301, fetch_redirect_response=True)

    def test_if_logout_works(self):
        user = create_user()
        user.set_password('test')
        user.save()
        c = Client()
        response = c.post(reverse('log_in'), {'username': 'test_user', 'password': 'test'})
        user = get_user(c)
        self.assertFalse(user.is_anonymous)
        response = c.get(reverse('log_out'))
        user = get_user(c)
        self.assertTrue(user.is_anonymous)

    def test_logout_page_fail(self):
        response = self.client.get(reverse('log_out'))
        self.assertNotEqual(response.status_code, 200)


class ProductsListViewTest(TestCase):
    pass


class SearchViewTest(TestCase):
    pass


class ProductDetailViewTest(TestCase):
    pass


class AddProductViewTest(TestCase):
    pass


class DeleteProductViewTest(TestCase):
    pass


class ConfirmProductDeletionViewTest(TestCase):
    pass


class EditProductViewTest(TestCase):
    pass


class AddProductToCartViewTest(TestCase):
    pass


class CartViewTest(TestCase):
    pass


class RemoveProductFromCartViewTest(TestCase):
    pass


class ConfirmOrderViewTest(TestCase):
    pass
