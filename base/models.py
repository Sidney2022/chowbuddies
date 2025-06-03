from django.db import IntegrityError, models
import uuid
from django.utils.text import slugify
from django.urls import  reverse
import random
from accounts.models import Producer, Profile
from datetime import datetime
from django.utils import timezone

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories')
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            super(ProductCategory, self).save(*args, **kwargs)
        else:
            self.slug = slugify(f'{self.name}-{self.id}')
            super(ProductCategory, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Product Categories'
    
    def __str__(self):
        return self.name.capitalize()


class Product(models.Model):
    prod_id = models.UUIDField(default=uuid.uuid4)
    category = models.ForeignKey("ProductCategory", related_name='products', on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product-imgs')
    name = models.CharField(max_length=255)
    price = models.FloatField()
    # unit_type = models.CharField(  
    #     max_length=255,
    #     choices=(
    #         ('unit', 'Unit'),
    #         ('kg', 'Kg'),
    #         ('g', 'G'),
    #         ('l', 'L'),
    #         ('ml', 'Ml'),
    #     ), default='unit'
    # )
    # qty_type = models.CharField(
        # max_length=255,
    #     choices=(
    #         ('piece', 'Piece'),
    #         ('bottle', 'Bottle'),
    #         ('packet', 'Packet'),
    #         ('box', 'Box'),
    #         ('carton', 'Carton'),
    #         ('bag', 'Bag'),
    #         ('basket', 'Basket'),
    #     ), default='piece'
    # )
    discount = models.PositiveIntegerField( default=0)
    no_stock = models.PositiveIntegerField(default=5)
    description = models.TextField()
    status = models.CharField(
        max_length=255,
        choices=(
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ), default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    variations = models.JSONField(null=True, blank=True)
    is_deleted =models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)

    def selling_price(self):
        if not self.price == 0:
            discount_value = ( self.price * self.discount ) / 100
            discount_price = self.price - discount_value
            return discount_price
        return self.price

    def colors(self):
        return [color for color in self.variations['colors'].split(',')]
    
    def sizes(self):
        return [size for size in self.variations['sizes'].split(',')]

    # def save(self, *args, **kwargs):
    #     if  self.id:
    #         self.slug = slugify(f'{self.name}-{self.id}')
    #     super(Product, self).save(*args, **kwargs)
   
   
    def get_absolute_url(self):
        return reverse("product-detail" ,kwargs={"slug":self.slug})

    def get_product_images(self):
        return ProductImage.objects.filter(product_id=self.id)
    
    def in_stock(self):
        if self.no_stock == 0:
            return False
        return True

    # def get_product_reviews(self):
    #     return ProductReview.objects.filter(product=self.id)    

    def product_rating(self):
        reviews = self.get_product_reviews()
        total_rating=0
        for review in reviews:
            total_rating += review.rating
        if not total_rating: return 0
        avg_rating = total_rating/len(reviews)
        return {"avg_rating":avg_rating, 'no_reviews':len(reviews)}

    def __str__(self):
        return self.name

    def status_badge(self):
        if self.status == 'published': color = 'success'
        elif self.status == 'draft':  color = 'secondary'
        else : color = 'danger'
        return color
    
    class Meta:
        ordering = ['-created_at']


class ProductImage(models.Model):
    product_id = models.ForeignKey(Product, related_name='product_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product-imgs')


class Cart(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True) #remove this field

    def get_cart_items(self):
        items = CartItem.objects.filter(cart=self.id)

        return items
    def get_cart_products(self):
        return [item.product for item in self.get_cart_items() ]

    def total_amount(self):
        total = 0
        for item in self.get_cart_items():
            total += item.item_cost()
        return total
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default='', blank=True, null=True)
    color = models.CharField(max_length=10, default='', blank=True, null=True)
    
    def cart_user(self):
        return self.cart.user.email
    
    def item_cost(self):
        return self.product.selling_price() * self.quantity


class WishList(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField( Product, related_name='wishlists')
    time_stamp = models.DateTimeField(auto_now_add=True) #remove this field


class Order(models.Model):
    # add timestamp for payment completion
    order_id = models.CharField(max_length=10, unique=True, blank=True, editable=False, primary_key=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    amount = models.FloatField()
    payment_status = models.CharField(
        max_length=255,        
        choices=(
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
        ), default='unpaid' )
    order_status = models.CharField(
        max_length=255,
        choices=(
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ), default='pending' )
    shipped = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    shipped_at = models.DateTimeField(blank=True, null=True)
    edd = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    delivery_address=models.JSONField()
    class Meta:
        ordering = ['-created_at']


    def get_order_items(self):
        items = OrderItem.objects.filter(order=self.order_id)
        return items
    
    def payment_badge(self):
        if self.payment_status == 'unpaid': color = 'danger'
        elif self.payment_status == 'paid':  color = 'success'
        return color
    
    def status_badge(self):
        if self.order_status == 'delivered': color = 'success'
        elif self.order_status == 'cancelled':  color = 'danger'
        else : color = 'warning'
        return color
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_unique_order_id()
        super().save(*args, **kwargs)
    
    def total_amount(self):
        orderitems = OrderItem.objects.filter(order=self.order_id)
        total=0
        for _ in orderitems:
            total +=_.get_cost()
        return total
            

    def generate_unique_order_id(self):
        while True:
            # Generate a random 6-digit number and prefix it with '1'
            order_id = '1' + ''.join(random.choices('0123456789', k=9))
            if not Order.objects.filter(order_id=order_id).exists():
                return order_id
            
    def can_be_cancelled(self):
        if self.order_status == 'pending':
            return True
        return False
    
    def can_be_returned(self):
        if self.order_status == 'delivered' and self.delivered_at+datetime.timedelta(days=7) > datetime.datetime.now():
            return True
        return False


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, default='')
    color = models.CharField(max_length=10, default='')

    def get_cost(self):
        return self.price * self.quantity


class ProductReview(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='product_reviewer')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveIntegerField() #(default=1, validators=[validate_review_rating])
    title = models.CharField(max_length=255)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    

class Notification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_notifications')
    title = models.CharField(max_length=255, default='')
    message = models.TextField()
    is_opened = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=50, default='')

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.title}-{self.id}")
        super(Notification, self).save(*args, **kwargs)

    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active   # Return time in secs 
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time 
    
    class Meta:
        ordering = ['-id']
        
    def __str__(self):
        return f"{self.title} - {self.user.email}"


class Wallet(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='user_wallet')
    amount = models.FloatField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.amount}"
    
    def add_money(self, amount):
        self.amount += amount
        self.save()
        
    def deduct_money(self, amount):
        if self.amount >= amount:
            self.amount -= amount
            self.save()
        else:
            raise ValueError("Insufficient funds in wallet")
        
    def get_balance(self):
        return self.amount
    
    def transaction_history(self):
        return WalletTransaction.objects.filter(wallet=self.id)
    
    
class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.FloatField()
    transaction_type = models.CharField(
        max_length=255,
        choices=(
            ('credit', 'Credit'),
            ('debit', 'Debit'),
        )
    )
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.wallet.user.email}"
    
    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time
    
    class Meta:
        ordering = ['-date_created']
        
        
class VideoTutorial(models.Model):
    title = models.CharField(max_length=255)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='video_tutorials')
    description = models.TextField()
    video_url = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title
    
    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time
    

class VideoComment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='video_comments')
    video = models.ForeignKey(VideoTutorial, on_delete=models.CASCADE, related_name='video_comments')
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment[:20]
    
    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time
    class Meta:
        ordering = ['-date_created']


class DisLikedVideo(models.Model):
    video = models.ForeignKey(VideoTutorial, on_delete=models.CASCADE, related_name='video_likes')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='video_likes')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tutorial.title} - {self.user.email}"
    
    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time
    
    
class LikedVideo(models.Model):
    video = models.ForeignKey(VideoTutorial, on_delete=models.CASCADE, related_name='video_dislikes')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='video_dislikes')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video.title} - {self.user.email}"
    
    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time
    class Meta:
        ordering = ['-date_created']
        
        
class SavedVideo(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='saved_videos')
    video = models.ForeignKey(VideoTutorial, on_delete=models.CASCADE, related_name='saved_videos')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video.title} - {self.user.email}"
    
    def time_sent(self):
        time_active =   datetime.now().timestamp() - self.date_created.timestamp()
        time =  time_active
        if time > 3600*24 :
            time /= (3600*24)
            msg_time = f"{int(time)} days ago"
        elif time > 3600 :
            time /= 3600
            msg_time = f"{int(time)} hrs ago"
        elif time > 60:
            time /= 60
            msg_time = f"{int(time)} mins ago"
        else:
            msg_time = f"{int(time)} secs ago"
        return msg_time
    class Meta:
        ordering = ['-date_created']
        
        
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question        




class Wallet(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='NGN')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Wallet"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('transfer', 'Transfer'),
        ('withdraw', 'Withdraw'),
    )
    wallet = models.ForeignKey(Wallet, null=True, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    paystack_payment_reference = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.status}"


class PaymentMethod(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    bank_name = models.CharField( max_length=255)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField( max_length=10)
    
    
    
class UserLog(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    action = models.CharField(max_length=255) 
    timestamp=models.DateTimeField(auto_now_add=True)
    
    def get_action_description(self):
        text = f"user, {self.user } {self.action} at {self.timestamp}"
        return text


# in-app support
# do i make a model for this or use a third party service
# if i decide to build, i need to manage the db, push notifications, and maybe email







