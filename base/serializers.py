from base.models import  ProductCategory,Product, ProductImage, Cart, CartItem, Order, OrderItem,  ProductReview, Notification, SavedVideo, VideoTutorial, LikedVideo, DisLikedVideo, VideoComment, FAQ, PaymentMethod #,  WaitList, NewsLetter,FAQ
from accounts.models import Profile, Producer , ShippingInfo
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError, PrimaryKeyRelatedField
import requests
from rest_framework import serializers
from .models import Wallet, WalletTransaction
from django.db.models import Sum
from django.http import JsonResponse

class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment', 'product', 'user', 'title']
        # read_only_fields = [ 'user']

    def create(self, validated_data):
        return super().create(validated_data)


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']
        # read_only_fields = ['product', 'id']


class ProductSerializer(ModelSerializer):
    product_images = ProductImageSerializer(many=True, read_only=True)
    product_reviews = ProductReviewSerializer(many=True, read_only=True)
    # producer_name = SerializerMethodField()
    category = PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
    productCategory = SerializerMethodField()
    class Meta:
        model = Product
        fields = "__all__"
        
    # def get_producer_name(self, obj):
    #     # Assuming 'related_field' is the ForeignKey field in your model
    #     return obj.producer.user_id.first_name #first_name
    def get_productCategory(self, obj):
        # Assuming 'related_field' is the ForeignKey field in your model
        return obj.category.name #first_name
    
    def validate_category(self, value):
        # If value comes as a string (e.g., "3"), convert it to int
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return value

    def create(self, validated_data):
        # Extract images data
        images_data = validated_data.pop('product_images', [])
        
        # Create Product instance
        product = Product.objects.create(**validated_data)
        
        # Create ProductImage instances
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        return product


class ProductCategorySerializer(ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCategory
        fields = "__all__"


class ShippingInfoSerializer(ModelSerializer):

    class Meta:
        model = ShippingInfo
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('email', 'password', 'phone')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Profile.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            first_name='',  
            last_name=''    
        )
        return user
    
class ProfileSerializer(ModelSerializer):
    # shipping_info = ShippingInfoSerializer(read_only=True)
    order_history = SerializerMethodField()
    isProducer = SerializerMethodField()
    wallet = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('id',  'first_name', 'last_name', 'email', 'password','phone', 'is_staff', 'shipping_info', "profileImage","isProducer",
                  "order_history", "date_joined", "last_login", "wallet")
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True,}, 'last_name': {'read_only': True},
                        'is_staff': {'read_only': True}, 'shipping_info':{'read_only':True}, "isProducer":{'read_only':True}, "wallet":{"read_only":True} }
    
    def validate(self, data):
        if self.instance and (not data.get('first_name', self.instance.first_name) or not data.get('last_name', self.instance.last_name)):
            raise ValidationError("First or last name cannot be blank.")
        return data
    
    
    def get_wallet(self, obj):
        try:
            wallet = Wallet.objects.get(user=obj)
            return WalletSerializer(wallet, context=self.context).data
        except Wallet.DoesNotExist as err:
            print(err)
            return None  # Or return a default serialized response
        except Wallet.MultipleObjectsReturned as e:
            print(e)
            # Log error or handle as needed
            return None
        
    def get_shipping_info(self, obj):
        return ShippingInfo.objects.filter(user=obj.id)
    
    def get_isProducer(self, obj):
        return Producer.objects.filter(id=obj.id).exists()
    
    def get_order_history(self, obj):
        orders = Order.objects.filter(user=obj.id)
        order_items = []
        # for order in orders:
        #     order_items.extend(OrderItem.objects.filter(order=order.order_id))
        return OrderSerializer(orders, many=True).data
    
    
class PaymentMethodSerializer(ModelSerializer):
    class  Meta:
        model = PaymentMethod
        fields = "__all__"   


class ProducerSerializer(ModelSerializer):
    class Meta:
        model = Producer
        fields = "__all__"

    # def validate(self, data):
    #     if self.instance is None and "user_id" not in data:
    #         raise ValidationError({"user_id":"this field is required"})
    #     return data


class CartItemSerializer(ModelSerializer):
    # product = SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'cart', 'quantity', ]
    
    # def get_product(self, obj):
    #     product =  Product.objects.get(slug=obj.product.slug)
    #     return ProductSerializer(product).data

   
class CartSerializer(ModelSerializer):
    cart_items = CartItemSerializer(read_only=True, many=True)

    class Meta:
        model = Cart
        fields = ['user', 'cart_items']


class OrderItemSerializer(ModelSerializer):
    product_name = SerializerMethodField()
    product = SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = '__all__'
    def get_product_name(self, obj):
        # Assuming 'related_field' is the ForeignKey field in your model
        return obj.product.name #first_name
    def get_product(self, obj):
    # Assuming 'related_field' is the ForeignKey field in your model
     return {
        "name": f"{obj.product.name}",
        "image":f"http://localhost:9000{obj.product.image.url}",
        "id":obj.product.prod_id,
        # "rating":obj.product.product_rating().avg_rating,
        "price":obj.product.price,
    }
    

class OrderSerializer(ModelSerializer):
    order_items = OrderItemSerializer(read_only=True, many=True)
    user = SerializerMethodField()
    total_amount = SerializerMethodField()

    
    def get_user(self, obj):
        return {
            "name": f"{obj.user.first_name} {obj.user.last_name}",
            "email":obj.user.email,
            "id":obj.user.id,
            "profileImage":f"http://localhost:9000{obj.user.profileImage.url}"
        }
    def get_total_amount(self, obj):
        return  obj.total_amount()
        
        
    class Meta:
        model = Order
        fields = "__all__"


class NotificationSerializer(ModelSerializer):
    userName = SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = "__all__"
        
    def get_userName(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class VideoTutorialSerializer(ModelSerializer):
    class Meta:
        model = VideoTutorial
        fields = "__all__"
        
        
class VideoCommentSerializer(ModelSerializer):
    class Meta:
        model = VideoComment
        fields = "__all__"
        
        
class LikedVideoSerializer(ModelSerializer):
    class Meta:
        model = LikedVideo
        fields = "__all__"
        
        
class DisLikedVideoSerializer(ModelSerializer):
    class Meta:
        model = DisLikedVideo
        fields = "__all__"
        

class SavedVideoSerializer(ModelSerializer):
    class Meta:
        model = SavedVideo
        fields = "__all__"


class FAQSerializer(ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"
        

class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    depositTxns = SerializerMethodField()
    
    def get_balance(self, obj):
        balance = WalletTransaction.objects.filter(
            wallet=obj, status='success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return balance

    class Meta:
        model = Wallet
        fields = ['id', 'currency', 'balance', 'depositTxns']
    
    def get_depositTxns(self, obj):
        try:
            wallet = Wallet.objects.get(user=obj.user)
            txns = WalletTransaction.objects.filter(wallet=wallet, transaction_type="deposit")
            return WalletTransactionSerializer(txns, many=True).data
        except Wallet.DoesNotExist as err:
            print(err)
            return None  
        except Wallet.MultipleObjectsReturned as e:
            print(e)
            return None
        
 
class WalletTransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WalletTransaction
        fields = "__all__"
 
 
class DepositSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    email = serializers.EmailField(write_only=True)
    txns = SerializerMethodField()
    
    class Meta:
        model = WalletTransaction
        fields = ['txns']
    
    def get_txns(self, obj):
        return WalletTransaction.objects.filter(transaction_type=obj.transaction_type)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_email(self, value):
        if not Profile.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email not found.")
        return value

    def save(self):
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)
        data = self.validated_data
        from django.conf import settings
        import requests

        # Initialize Paystack transaction
        reference=f"chowbuddies-{user.id}-{int(data['amount'] * 100)}"
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
        payload = {
            "reference": reference,
            'email': data['email'],
            'amount': int(data['amount'] * 100),  # Convert to kobo (Paystack uses subunits)
            'callback_url':  f'{settings.PAYSTACK_WEBHOOK_DOMAIN}/api/v1/verify-payment/?reference={reference}',
        }
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        if response_data.get('status'):
            # Create transaction record
            transaction = WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='deposit',
                amount=data['amount'],
                paystack_payment_reference=response_data['data']['reference'],
                status='pending'
            )
            return response_data
        else:
            raise serializers.ValidationError("Failed to initialize transaction.")






