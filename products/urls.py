from django.urls import path


from .views import add_product, add_product_to_cart, cart, confirm_order, confirm_product_deletion, delete_product, \
    edit_product, log_in, log_out, product_detail, products_list, remove_product_from_cart, search

urlpatterns = [
    path('log_in/', log_in, name='log_in'),
    path('log_out/', log_out, name='log_out'),
    path('', products_list, name='products_list'),
    path('add/', add_product, name='add_product'),
    path('search/', search, name='search'),
    path('details/<slug>', product_detail, name='product_detail'),
    path('confirm_deletion/<slug>', confirm_product_deletion, name='confirm_product_deletion'),
    path('delete/<slug>', delete_product, name='delete_product'),
    path('edit/<slug>', edit_product, name='edit_product'),
    path('cart/', cart, name='cart'),
    path('add_to_cart/<slug>', add_product_to_cart, name='add_product_to_cart'),
    path('remove_from_cart/<slug>', remove_product_from_cart, name='remove_product_from_cart'),
    path('confirm_order/', confirm_order, name='confirm_order'),
]