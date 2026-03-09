from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from datetime import datetime
from django.utils.timezone import now
import uuid
from datetime import datetime, timedelta
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
# from phonenumber_field.modelfields import PhoneNumberField               # type: ignore
import random


def validate_address_json(value):
    required_fields = {
        'address': str,
        'state': str,
        'city': str,
        'phone': int,
        'first_name': str,
        'last_name': str
    }
    # Ensure the value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError("Invalid JSON data, must be a dictionary")
    # Check for required keys and their types
    for key, expected_type in required_fields.items():
        if key not in value:
            raise ValidationError(f"Missing key in JSON data: {key}")
        if not isinstance(value[key], expected_type):
            raise ValidationError(f"Incorrect type for key '{key}': expected {expected_type.__name__}, got {type(value[key]).__name__}")


class ProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Profile(AbstractUser):
    """ custom user model """

    email = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=255, blank=False , null=False )
    last_name  = models.CharField(max_length=255, blank=False , null=False )
    connected_devices = models.JSONField(blank=True, null=True)
    username = models.CharField(max_length=100, unique=False, null=True, blank=True)
    default_shipping_address = models.ForeignKey( 'ShippingInfo', on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=13)
    is_deleted = models.BooleanField(default=False)
    profileImage = models.ImageField(default="profiles/blank-profile.png", upload_to="profiles")
    is_active = models.BooleanField(default=False)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ ]  

    objects = ProfileManager()
    def __str__(self):
        return self.email
    
    def get_user_orders(self):
        return self.orders.all()

    def amount_spent(self):
        total = 0
        for order in self.get_user_orders():
            total += order.amount
        return total


class Producer(models.Model):
    user_id = models.OneToOneField("Profile", related_name='producer', on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_location = models.JSONField()
    is_verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=255,
        choices=(
            ('pending', 'Pending'),
            ('active', 'Active'),
            ('blacklisted', 'Blacklisted'),
        ), default='pending'
    )
    def __str__(self):
        return f"{self.user_id.email} - {self.business_name}"
    

class ShippingInfo(models.Model):
    user = models.ForeignKey(Profile, related_name='shipping_info', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    directions = models.CharField(max_length=255, null=True, blank=True)
    # phone = PhoneNumberField(max_length=13)
    last_updated = models.DateTimeField(auto_now=True)


class PasswordResetRequest(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=128, default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def token_valid(self):
        time_sent =   datetime.now().timestamp() - self.created_at.timestamp()
        time_in_hrs = time_sent/(60*60) 
        if time_in_hrs > 2:
            return False
        return True 

    
def generate_random_id():
    return str(random.randint(1000, 9999))


class VerifyEmailToken(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    token = models.CharField(max_length=4, default=generate_random_id, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    

    def token_valid(self):
        time_sent =   datetime.now().timestamp() - self.created_at.timestamp()
        time_in_hrs = time_sent/(60) 
        print(f'time sent is {time_sent} and time in hrs is {time_in_hrs}')
        if time_in_hrs > 2:
            return False
        else:
            return True 




