from base.models import Cart, CartItem, Order, OrderItem, UserLog
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


def get_cart(user):
    """Helper method to get or create a cart for the user."""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def create_log(user, action ):
    try:
        action = action
        log = UserLog.objects.create(user=user, action=action)
        log.save()
    except Exception as e:
        print(e)
        
    
# class CustomLogger():
#     def create_log(self, user, action ):
#         try:
#             action = action
#             log = UserLog.objects.create(user=user, action=action)
#             log.save()
#         except Exception as e:
#             print(e)
            
#     def get_logs(self, user ):
#         try:
#             action = action
#             log = UserLog.objects.create(user=user, action=action)
#             log.save()
#         except Exception as e:
#             print(e)



def send_email_funct( subject, recipient, context, template_name):
    try:
        subject = subject
        html_message = render_to_string(f'email/{template_name}.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, f"Chowbuddies <{settings.DEFAULT_FROM_EMAIL}>", [recipient], html_message=html_message
            )
    except Exception as e:
        print(e)