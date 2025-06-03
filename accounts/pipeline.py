
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import Profile  

def notify_user_for_linking(backend, details, user=None, *args, **kwargs):
    email = details.get('email')

    # Check if the email is registered but not linked to a social account
    if email and Profile.objects.filter(email=email, social_auth__isnull=True).exists():
        request = kwargs.get('request')
        
        # Store necessary data in the session to handle linking or password sign-in
        request.session['social_email'] = email
        request.session['backend'] = backend.name

        # Redirect to a custom page for the user to decide
        return redirect(reverse('link_account')+f"?email={email}")  # Custom view to handle the decision

    return None







