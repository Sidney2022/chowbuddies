# from celery import shared_task
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


# from_email=f"ChowBuddies <info@siddevlabs.icu>"
# @shared_task
# def send_email_task(subject, recipient_list, email_template, context):
#     print(from_email)
#     try:
#         print('preparing ......')
#         html_message = render_to_string(email_template, context)
#         plain_message = strip_tags(html_message)
#         print('preparing to send......')
#         # send_mail(
#         #     subject, plain_message, from_email, recipient_list, html_message=html_message
#         #     )
#         print('email sent')
#     except Exception as e:
#         # log error to a file or create admin notification
#         print(e)
#         print("email not sent")
#         pass
    
from_email=f"ChowBuddies <info@siddevlabs.icu>"
# @shared_task
def send_email_task(subject, recipient_list, context):
    print(from_email)
    try:
        print('preparing ......')
        html_message = render_to_string( context)
        plain_message = strip_tags(html_message)
        print('preparing to send......')
        # send_mail(
        #     subject, plain_message, from_email, recipient_list, html_message=html_message
        #     )
        print('email sent')
    except Exception as e:
        # log error to a file or create admin notification
        print(e)
        print("email not sent")
        pass




