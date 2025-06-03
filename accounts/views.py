from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import auth
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views import View
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from .models import  PasswordResetRequest, VerifyEmailToken
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
# from base.monnify import Monnify
from django.views.decorators.cache import cache_page
from django.core.cache import cache
# from api.tasks import send_email_task
import random, os
from base.models import Cart, CartItem
from django.utils import timezone
from datetime import timedelta

from dotenv import load_dotenv # type: ignore
load_dotenv()

# from social_django.models import UserSocialAuth


# Initialize environment variables
# env = environ.Env()
# environ.Env.read_env()
site_name=os.getenv("site_name")


def generate_token(user:Profile):
    number=random.randint(10000, 99999)
    token = VerifyEmailToken.objects.create(user=user, token=number )
    token.save()
    return token


def val_email(email):
    try:
        validate_email(email)
        return True
    except Exception as e:
        return False
    

def val_pw(password, request):
    try:
        validate_password(password)
        return True
    except Exception as e:
        messages.error(request, f'{e}')
        return False


class SignIn(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('homepage')
        redirect_page = request.GET.get("next")
        return render(request, 'auth/signin.html', {"redirect_page":redirect_page})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('homepage')
        email=request.POST['email'].strip().lower()
        next_page = request.POST['next'].lower().strip()
        session_key = request.session.session_key
        user = auth.authenticate(
            email=email, 
            password=request.POST['password'], )
        user_profile=Profile.objects.filter(email=email).first()
        if user and user.is_active:
            auth.login(request, user)
            if next_page.lower() != 'none':
                redirect_url = next_page
            else:
                redirect_url = '/'
            if session_key:
                cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
                user_cart, created = Cart.objects.get_or_create(user=user_profile)
                for item in cart.get_cart_items():
                    user_cart_item = CartItem.objects.filter(cart=user_cart, product=item.product).first()
                    if user_cart_item:
                        user_cart_item.quantity += item.quantity
                        user_cart_item.save()
                    else:
                        item.cart = user_cart
                        item.save()
                cart.delete()
            return redirect(redirect_url)
        elif user_profile and user_profile.is_active ==False:
            context={"message":"Your account has not been verified. Pls check your email or use the form below to request a new link"
                     }
            return redirect('send_otp')
        else:
            messages.info(request, 'invalid login credentials')
        return redirect('signin')

       
class SignUp(View):
    def get(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
        #     return redirect('homepage')        
        return render(request, 'auth/signup.html')

    def post(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
        #     return redirect('homepage')
        first_name= request.POST['first_name'].strip().lower()
        last_name= request.POST['last_name'].strip().lower()
        email= request.POST['email'].strip().lower()
        password= request.POST['password']
        password2= request.POST['password2']
        phone= request.POST['phone'].lower()
        context = {"field_values":request.POST}
        if  not email or not password or not password2 or not first_name or not last_name or not phone:
            messages.info(request, 'fields cannot be blank!')
        elif Profile.objects.filter(email=email).exists():
            messages.info(request, 'email already in use. If this your account, please proceed to login')
        elif not val_email(email):
            messages.info(request, 'please enter a valid email address')
        elif password != password2:
            messages.error(request, 'passwords do not match!')
        elif not val_pw(password, request):
            pass
        else:
            
            new_profile = Profile.objects.create_user( email=email, password=password, first_name=first_name, last_name=last_name, phone=phone)
            new_profile.is_active = False
            new_profile.save()
            messages.info(request, 'Account created. Please verify your email to proceed')
            token = generate_token(new_profile)
            link= f"https://{get_current_site(request)}/accounts/auth/verify-account/{token.token}"
            subject = f"Welcome to {site_name}"
            context = {"full_name":f'{first_name} {last_name}', "website_name":env("site_name"), "link":link,
                        "website_email":env("site_email"), "token":f"{token.token}", "comp_address":env("comp_address")
            }
            # send_email_task.delay(subject=subject, 
            # recipient_list= [email], email_template='email/welcome.html', context=context)
            return redirect('acct-success')
        return render(request, 'auth/signup.html', context)


def send_verification_otp(request):
    if request.user.is_authenticated:
            return redirect('homepage')
    referer =  request.META.get("HTTP_REFERER")
    if request.method == "POST":
        email = request.POST['email'].strip().lower()
        if not email:
            messages.error(request, 'email cannot be blank')
            return redirect('send_otp')
        profile = get_object_or_404(Profile, email=email)
        if profile.is_active:
            messages.info(request, 'account already verified')
            return redirect('signin')
        token = generate_token(profile)
        messages.info(request, 'an otp code has been sent to your email')
        link= f"https://{get_current_site(request)}/accounts/auth/verify-account/{token.token}"
        print(link)
        subject = f"Verify Account"
        context = {"website_name":env("site_name"), "link":link,
            "website_email":env("site_email"), "token":f"{token.token}", "comp_address":env("comp_address")
            }
        # send_email_task.delay(subject=subject, 
        # recipient_list= [email], email_template='email/verify_email.html', context=context)
        return redirect('otp-success')
    return render(request, 'auth/send-otp.html', {"referer":referer})


def verify_otp(request, token):
        if request.user.is_authenticated:
            return redirect('homepage')
        token = VerifyEmailToken.objects.filter(token=token).first()
        if not token or not token.token_valid() :
            messages.error(request, 'invalid token or token is expired. please request a new token')
            return redirect("send_otp") # send_otp url
        profile = get_object_or_404(Profile, email=token.user.email)
        if profile.is_active:
            messages.info(request, 'account already verified')
            return redirect('signin')
        profile.is_active = True
        profile.save()
        token.delete()
        messages.info(request, 'email verified. please login')
        context = {"website_name":env("site_name"),"website_email":env("site_email"), "comp_address":env("comp_address"),
                   "message":"Your account has been verified. if you do not recognize this activity, please contact us by replying to this message", "name":profile.first_name
            }
        # send_email_task.delay(subject="Account Verified",
        # recipient_list= [token.user.email], email_template='email/account-verified.html', context=context)
        return redirect('signin')


class SignOut(View):
    def get(self, request):
        auth.logout(request)
        return redirect('homepage')
    

class PasswordResetView(View):
    def get(self, request):
        return render(request, 'auth/resetpw.html')
    def post(self, request):
        email = request.POST['email'].lower().strip()
        if not email:
            messages.error(request, 'email cannot be blank!')
            return redirect('password_reset')
        user = Profile.objects.filter(email=email).first()
        if user:
            new_token  = PasswordResetRequest.objects.create(email=email)
            new_token.save()
            link = f"{get_current_site(request)}/accounts/auth/reset-password/{new_token.token}"
            context = {"user_email":email, "website_name":site_name,
                        "website_email":env("site_email"), "link":link, "comp_address":env("comp_address")
            }
            # send_email_task.delay(subject="Reset Password",  
            # recipient_list= [email], email_template='email/reset_password.html', context=context)
        return render(request, 'auth/success-page.html', {"message":"A password recovery mail was sent if an account was found for email. Please check your inbox"})


class ConfirmPasswordResetTokenView(View):
    def get(self, request, token):
        token = get_object_or_404(PasswordResetRequest, token=token)
        if not token.token_valid() or token.used == True:
            messages.error(request, 'invalid token or token is expired. enter your email below to receive a new link')
            return redirect('password_reset')
        user=get_object_or_404(Profile,email=token.email)
        return render(request, 'auth/set_pass.html', {"user_email":user, "token":token.token})

    def post(self,request,token):
        password = request.POST['password']
        password2 = request.POST['password2']
        token=get_object_or_404(PasswordResetRequest, token=token)
        if not password == password2:
            messages.error(request, 'passwords do not match')
            return redirect(reverse('confirm_password_token', args=[token.token]))
        elif not val_pw(password, request):
            return redirect(reverse('confirm_password_token', args=[token.token]))
        user = Profile.objects.filter(email=token.email).first()
        user.set_password(password)
        user.save()
        token.delete()
        subject = f"Welcome to {site_name}"
        context = {"website_name":env("site_name"),
                        "website_email":env("site_email"), "token":f"{token.token}", "comp_address":env("comp_address"),
                         "message":"Your password was changed. if this action was not requested by you, please contact us by replying to this message", "name":user.first_name
            }
        # send_email_task.delay(subject=subject, 
        # recipient_list= [user.email], email_template='email/verify_email.html', context=context)  
        messages.success(request, 'password has been changed successfully. login with your new password to access your account.')
        return redirect('signin')


def verify_account_email(request, token):
    token = get_object_or_404(VerifyEmailToken, token=token)
    user = get_object_or_404(Profile, username=token.user.username)
    user.is_active = True
    user.save()
    messages.success(request, 'your account has been successfully activated')
    return redirect('homepage')


def account_create_success(request):
    message = {"message":"Your account has been created successfully. Please check your inbox for a verification link. "}
    return render(request, 'auth/success-page.html', message)


def send_otp_success(request):
    message = {"message":"A verification link has been sent to your mail. Please check your inbox. "}
    return render(request, 'auth/success-page.html', message)



def link_account(request):
    email = request.GET.get('email')
    backend = request.GET.get('backend')
    redirect_to = request.GET.get('next')

    # Ensure the email is provided
    if not email:
        return redirect('signin')  # Redirect to sign-in if no email is passed

    try:
        # Fetch the user using the custom Profile model by email
        user = Profile.objects.get(email=email)
    except Profile.DoesNotExist:
        return redirect('signin')  # Redirect if no user is found

    if request.method == 'POST':
        if 'link_google' in request.POST:
            # Handle linking the account by creating a UserSocialAuth entry
            uid = request.POST.get('uid')  # UID should come from Google OAuth response

            # Create a social auth record for the user
            UserSocialAuth.objects.create(user=user, provider="google-oauth2", uid=user.email)
            user.backend = 'social_core.backends.google.GoogleOAuth2'
            auth.login(request, user)
            # Redirect the user after successful account linking
            url = '/' if not redirect_to else redirect_to
            return redirect(url)  # Redirect to profile after linking

        elif 'continue_with_password' in request.POST:
            # Redirect to the sign-in page with a `next` parameter
            return redirect(reverse('signin') + f'?next={redirect_to}')

    return render(request, 'auth/link_account.html', {'email': email, 'backend': backend})


