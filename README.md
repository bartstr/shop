Simple shop with few basic capabilities written in Django.


Logged in users, can add products to cart, delete them from it, and order items from cart. Then they will receive email with order confirmation and invoice.

Users with flag is_staff can add new products to shop, delete them, they cannot add products to carts.


Users cannot register (I decided to not focus on usability like this, they still may be added via admin panel).


I used python 3.8 and django 3.2.5. All core packages you can find in requirements.txt.

Application is well covered with unittests.

To build templates I used one of Colorlib's (https://colorlib.com/wp/templates/) frontend shop template with few changes.
