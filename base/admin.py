from django.contrib import admin
from .models import Product, ProductCategory, Cart, CartItem, ProductImage, ProductReview, Order, OrderItem, VideoTutorial, VideoComment, LikedVideo, Notification, DisLikedVideo, SavedVideo, Notification
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from .models import Wallet, WalletTransaction


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'discount', 'producer', 'no_stock', 'created_at', 'updated_at' ]

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', "user",  "created_at", ]


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'time_stamp']
    
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity']



admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(ProductReview)
admin.site.register(ProductImage)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(LikedVideo)
admin.site.register(DisLikedVideo)
admin.site.register(VideoTutorial)
admin.site.register(VideoComment)
admin.site.register(SavedVideo)
admin.site.register(Notification)

admin.site.register(Wallet)
admin.site.register(WalletTransaction)