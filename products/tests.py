from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase
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


def create_client_address(user):
    return ClientAdress.objects.create(client=user, company='test company', tax_number=23, name='test name',
                                       surname='test surname', street='test street', zip_code='test zip code',
                                       city='test city', street_number='test street number',
                                       apartment_number='test apartment number')


class ClientAdressTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.address = create_client_address(cls.user)

    def test_client_adress_pass(self):
        record = ClientAdress.objects.get(client=self.user)
        self.assertTrue(isinstance(record, ClientAdress))
        self.assertTrue(isinstance(record.client, User))

    def test_client_adress_fail(self):
        record = ClientAdress.objects.get(client=self.user)
        self.assertFalse(record.client.username == 'another_name')


class ProductTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.product = create_product()

    def tearDown(self):
        delete_test_image()

    def test_product_pass(self):
        record = Product.objects.get(name=self.product.name)
        self.assertTrue(isinstance(record, Product))
        self.assertEqual(record.__str__(), record.name)

    def test_product_fail(self):
        record = Product.objects.get(name=self.product.name)
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

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()

    def test_login_page_pass(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        response = self.client.post(reverse('log_in'), {'username': self.user.username, 'password': 'test'})  # c
        user = get_user(self.client)
        self.assertEqual(user.username, self.user.username)
        self.assertFalse(user.is_anonymous)
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_fail(self):
        response = self.client.post(reverse('log_in'), {'username': 'another_username', 'password': 'password'})
        user = get_user(self.client)
        self.assertNotEqual(user.username, 'another_username')
        response = self.client.get(reverse('log_in'))
        self.assertNotIn('auth.user', response.context)


class LogoutViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()

    def test_logout_page_pass(self):
        response = self.client.get(reverse('log_out'))
        self.assertRedirects(response, expected_url='/products/log_in?next=/products/log_out/',
                             status_code=302, target_status_code=301, fetch_redirect_response=True)

    def test_if_logout_works(self):
        self.client.login(username=self.user.username, password='test')
        user = get_user(self.client)
        self.assertFalse(user.is_anonymous)
        response = self.client.get(reverse('log_out'))
        user = get_user(self.client)
        self.assertTrue(user.is_anonymous)

    def test_logout_page_fail(self):
        response = self.client.get(reverse('log_out'))
        self.assertNotEqual(response.status_code, 200)


class ProductsListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.product = create_product()

    def tearDown(self):
        delete_test_image()

    def test_product_list_view_pass(self):
        response = self.client.get(reverse('products_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_list_view_fail(self):
        response = self.client.get(reverse('products_list'))
        self.assertFalse('products' not in response.context)


class SearchViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.product = create_product()

    def tearDown(self):
        delete_test_image()

    def test_search_view_pass(self):
        response = self.client.get(reverse('search'))
        self.assertIn('form', response.context)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('search'), {'phrase': 'test'})
        self.assertContains(response, self.product.name)

    def test_search_view_fail(self):
        response = self.client.get(reverse('search'))
        self.assertNotEqual(response.context, [])


class ProductDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.product = create_product()
        record = Product.objects.get(name=cls.product.name)
        cls.slug = record.slug

    def tearDown(self):
        delete_test_image()

    def test_product_detail_view_pass(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_detail_view_fail(self):
        response = self.client.get('/details/No_such_product')
        self.assertNotEqual(response.status_code, 200)


class AddProductViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(username='test_super_user', email='test_user_email@email.com')
        cls.super_user.set_password('test')
        cls.super_user.save()
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()

    def tearDown(self):
        delete_test_image()

    def test_add_product_view_pass(self):
        self.client.login(username=self.super_user.username, password='test')
        user = get_user(self.client)
        self.assertEqual(user.is_superuser, True)
        response = self.client.get(reverse('add_product'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        response = self.client.get(reverse('products_list'))
        self.assertNotContains(response, 'Test item name')
        data = {'name': 'Test item name', 'producer': 'test_producer', 'description': 'test description', 'price': 3.2,
                'image': SimpleUploadedFile(name='test_image.jpg',
                                            content=open('media/images/test_image.jpg', 'rb').read(),
                                            content_type='image/jpeg')}
        response = self.client.post(reverse('add_product'), data)
        response = self.client.get(reverse('products_list'))
        self.assertContains(response, 'Test item name')

    def test_add_product_view_fail(self):

        self.client.login(username=self.user, password='test')
        response = self.client.get(reverse('add_product'), follow=True)
        self.assertEqual(response.status_code, 403)


class DeleteProductViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(username='super_user', email='test_user_email@email.com')
        cls.super_user.set_password('test')
        cls.super_user.save()
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()
        cls.product = create_product()
        cls.slug = cls.product.slug

    def tearDown(self):
        delete_test_image()

    def test_delete_product_view_pass(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        self.client.login(username='super_user', password='test')
        response = self.client.get(reverse('delete_product', args=[self.slug]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 404)

    def test_delete_product_view_fail(self):
        self.client.login(username='test_user', password='test')
        response = self.client.get(reverse('delete_product', args=[self.slug]))
        self.assertEqual(response.status_code, 403)


class ConfirmProductDeletionViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(username='super_user', email='test_user_email@email.com')
        cls.super_user.set_password('test')
        cls.super_user.save()
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()
        cls.product = create_product()
        cls.slug = cls.product.slug

    def tearDown(self):
        delete_test_image()

    def test_confirm_product_deletion_view_pass(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        self.client.login(username='super_user', password='test')
        response = self.client.get(reverse('confirm_product_deletion', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Czy na pewno') # TODO when translating app change it!

    def test_confirm_product_deletion_view_fail(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('confirm_product_deletion', args=[self.slug]))
        self.assertNotEqual(response.status_code, 200)
        self.client.login(username='test_user', password='test')
        response = self.client.get(reverse('confirm_product_deletion', args=[self.slug]))
        self.assertNotContains(response, 'Czy na pewno')


class EditProductViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create_superuser(username='super_user', email='test_user_email@email.com')
        cls.super_user.set_password('test')
        cls.super_user.save()
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()
        cls.product = create_product()
        cls.slug = cls.product.slug

    def tearDown(self):
        delete_test_image()

    def test_edit_product_view_pass(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        self.client.login(username='super_user', password='test')
        response = self.client.get(reverse('edit_product', args=[self.slug]))
        self.assertEqual(response.status_code, 200)

    def test_edit_product_view_fail(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('edit_product', args=[self.slug]))
        self.assertNotEqual(response.status_code, 200)
        self.client.login(username='test_user', password='test')
        response = self.client.get(reverse('edit_product', args=[self.slug]))
        self.assertNotEqual(response.status_code, 200)


class AddProductToCartViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()
        cls.product = create_product()
        cls.slug = cls.product.slug

    def tearDown(self):
        delete_test_image()

    def test_add_product_to_cart_view_pass(self):
        response = self.client.get(reverse('product_detail', args=[self.slug]))
        self.assertEqual(response.status_code, 200)
        self.client.login(username='test_user', password='test')
        response = self.client.get(reverse('add_product_to_cart', args=[self.slug]), follow=True)
        self.assertRedirects(response, reverse('cart'), 302)
        self.assertContains(response, self.product.name)

    def test_add_product_to_cart_view_fail(self):
        response = self.client.get(reverse('add_product_to_cart', args=[self.slug]), follow=True)
        self.assertNotContains(response, self.product.name)


class CartViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()

    def test_cart_view_pass(self):
        self.client.login(username='test_user', password='test')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'koszyk')  # TODO change while translating app

    def test_cart_view_fail(self):
        response = self.client.get(reverse('cart'))
        self.assertNotEqual(response.status_code, 200)


class RemoveProductFromCartViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()
        cls.product = create_product()
        cls.slug = cls.product.slug

    def tearDown(self):
        delete_test_image()

    def remove_product_from_cart_view_pass(self):
        self.client.login(username='test_user', password='test')
        self.client.get(reverse('add_product_to_cart', args=[self.slug]))
        response = self.client.get(reverse('cart'))
        self.assertContains(response, self.product.name)
        self.client.get(reverse('remove_product_from_cart', args=[self.slug]))
        response = self.client.get(reverse('cart'))
        self.assertContains(response, 'pusty')  # TODO translation

    def remove_product_from_cart_view_fail(self):
        self.client.get(reverse('remove_product_from_cart', args=[self.slug]))
        response = self.client.get(reverse('cart'))
        self.assertNotContains(response, 'pusty')  # bad test


class ConfirmOrderViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = create_user()
        cls.user.set_password('test')
        cls.user.save()
        cls.address = create_client_address(cls.user)
        cls.product = create_product()
        cls.slug = cls.product.slug

    def tearDown(self):
        delete_test_image()

    def confirm_order_view_pass(self):
        self.client.login(username='test_user', password='test')
        self.client.get(reverse('add_product_to_cart', args=[self.slug]))
        response = self.client.get(reverse('confirm_order'))
        self.assertEqual(response.status_code, 200)
        # TODO check invoice

    def confirm_order_view_fail(self):
        response = self.client.get(reverse('confirm_order'))
        self.assertNotEqual(response.status_code, 200)
