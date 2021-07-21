from django.core.mail import EmailMessage
from django.template.loader import get_template, render_to_string

from io import BytesIO
from xhtml2pdf import pisa

from shop.settings import DEFAULT_VENDOR


def create_invoice(template_src, order, client):
    products = order.products.all()
    args = {'products': products, 'order': order, 'client': client, 'vendor': DEFAULT_VENDOR}
    template = get_template(template_src)
    html = template.render(args)
    result = open('temp/invoices/invoice_{}.pdf'.format(order.id), 'wb')
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding="UTF-8")
    result.close()


def send_email_with_invoice(order):
    email_subject = 'Orderd confirmation - Bart Strzyga shop'
    email_body = render_to_string(
        'email/order_confirmation.txt', {
            'payment_time': order.payment_time, 'value': order.value, 'products': order.products.all()
        }
    )
    content = open('temp/invoices/invoice_{}.pdf'.format(order.id), 'rb')
    attachments = [('invoice_{}.pdf'.format(order.id), content.read(), 'application/pdf')]
    content.close()
    email = EmailMessage(subject=email_subject, body=email_body, from_email='kontakt@poukladana.pl',
                         to=[order.user.email], attachments=attachments)
    email.send()
