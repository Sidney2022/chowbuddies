from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response 
from rest_framework.views import APIView 
from .models import Product, ProductCategory, ProductImage, ProductReview, Cart,  CartItem, Order, OrderItem, FAQ, VideoTutorial, VideoComment, LikedVideo, DisLikedVideo, SavedVideo, Notification, Wallet, WalletTransaction, PaymentMethod
from accounts.models import Producer, Profile, VerifyEmailToken
from .serializers import ProducerSerializer, FAQSerializer, ProductSerializer, ProfileSerializer, VideoCommentSerializer, ProductCategorySerializer, CartSerializer, VideoTutorialSerializer, NotificationSerializer, ProductReviewSerializer, CartItemSerializer, OrderSerializer, SavedVideoSerializer, LikedVideoSerializer, DisLikedVideoSerializer, WalletSerializer, PaymentMethodSerializer, RegisterSerializer
from rest_framework import status, mixins, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import BasePermission
from .utils.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsAdminOrSuperuser, IsAdminOrSelf
from .utils.conversions import NumberConverter
from rest_framework.serializers import ValidationError
from django.db.models import Avg, Count, Q
from .utils.generic import get_cart, create_log
from django.conf import settings
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .utils.generic import send_email_funct

class HomePage(APIView):
    def get(self, request):
        context = {
            "message" : "Welcome to the Chowbuddies API server"
        }
        return Response(context, status=200  )


class ProfileView(mixins.ListModelMixin,   mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    

class ProfileDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): 
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'id'
    
   

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        print(self.request.user)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # create_log()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    
class UserTxnsView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): 
    permission_classes = [IsAuthenticated]
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    # lookup_field = 'id'
    
    def get_object(self):    
        return self.queryset.get(user=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 



class ProductCategoryView(mixins.ListModelMixin, mixins.CreateModelMixin,
                  generics.GenericAPIView): 
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

class ProductCategoryDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): 
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

  
class CartView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView): 
    serializer_class = CartItemSerializer
    permission_classes = [ IsAuthenticated ]
    queryset = CartItem.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        cart = get_cart(self.request.user)
        queryset = queryset.filter(cart = cart)
        return queryset   
                
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_data = request.data.copy()
        # print(f"submitted data - {request_data} {request_data.get('product_id')}")
        cart  = get_cart(self.request.user)
        product = Product.objects.get(id=request_data.get('product_id'))
        request_data['cart'] = cart.id
        request_data['product'] = product.id
        serializer = self.get_serializer(data=request_data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response( serializer.data , status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        

class CartDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): 
    permission_classes = [IsAuthenticated]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        cart = get_cart(self.request.user)
        queryset = queryset.filter(cart__user = self.request.user, cart=cart)
        return queryset 
  
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data_to_update = {'quantity': request.data.get('quantity') }#, 'cart': get_cart(self.request.user).id}
        serializer = self.get_serializer(instance, data=data_to_update, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response( serializer.data , status=status.HTTP_200_OK)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # i only want to update quantity. while updating quantity, evaluate if product is still in stock for quantity being added
        
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    
class ProductView(mixins.ListModelMixin, mixins.CreateModelMixin,
                  generics.GenericAPIView): 
    # permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
        
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            avg_rating=Avg('product_reviews__rating'),
            review_count=Count('product_reviews')
        )
        name = self.request.query_params.get('name', None)        
        category = self.request.query_params.get('category', None)        
        price_lte = self.request.query_params.get('price_lte', None)        
        price_gte = self.request.query_params.get('price_gte', None)   
        rating_lte = self.request.query_params.get('rating_lte', None)        
        rating_gte = self.request.query_params.get('rating_gte', None)   
            
        if name is not None:
            queryset = queryset.filter(name__icontains=name)  
        if category is not None:
            queryset = queryset.filter(category__name__icontains=category)  
        if price_gte is not None:
            queryset = queryset.filter(price__gte=NumberConverter.convert_to_float(price_gte))
        if price_lte is not None:
            queryset = queryset.filter(price__lte=NumberConverter.convert_to_float(price_lte))
        if rating_gte is not None:
            queryset = queryset.filter(avg_rating__gte=NumberConverter.convert_to_float(rating_gte))
        if rating_lte is not None:
            queryset = queryset.filter(avg_rating__lte=NumberConverter.convert_to_float(rating_lte))
        
            
        return queryset
        
    def get(self, request, *args, **kwargs):
        print("user accessing product list", request.user)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        producer = Producer.objects.filter(user_id=request.user.id).first()
        if not producer or producer and not producer.status == 'active':
            raise ValidationError({"message":"producer profile not found or is not active"})
        modified_data = request.data.copy()
        modified_data['producer'] = producer.id
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message":'product added', 'data': serializer.data }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return self.create(request, *args, **kwargs)
        

class ProductDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): # get single product, update single product
    permission_classes = [IsAuthenticated]#, IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'prod_id'

    def get(self, request, *args, **kwargs):
        
        return self.retrieve(request, *args, **kwargs)
 
    def put(self, request, *args, **kwargs):
        print(request.user.is_staff)
        product = self.get_object()
        if not product.producer.user_id.id == self.request.user.id and not request.user.is_staff: 
            raise ValidationError({"message": "you are not the owner of this product"})
        if product.is_deleted:  
            raise ValidationError({"message": "product is deleted"})
        if product.status != 'published':
            raise ValidationError({"message": "product is not published"})
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ProductReviewView(mixins.ListModelMixin, mixins.CreateModelMixin,  generics.GenericAPIView): 
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.request.method in ['GET', 'OPTIONS', 'HEAD']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def validate_product_param(self):
        product_uuid = self.kwargs.get('product_id', None)
        if product_uuid is None:
            raise ValidationError({"field": "product_id", "message": "This field is required."})
        product = Product.objects.filter(prod_id=product_uuid).first()
        if not product:
            raise ValidationError({"message": "product not found"})
        if product.is_deleted:  
            raise ValidationError({"message": "product is deleted"})
        if product.status != 'published':
            raise ValidationError({"message": "product is not published"})
        return product
        
    def get_queryset(self):
        queryset = super().get_queryset()
        product = self.validate_product_param()
        queryset = queryset.filter(product=product.id)  
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        product = self.validate_product_param()
        modified_data = request.data.copy()
        modified_data['product'] = product.id
        modified_data['user'] = request.user.id
        serializer = self.get_serializer(data=modified_data)
        
        if serializer.is_valid():
            rating = int(modified_data['rating'])
            user_prev_order = OrderItem.objects.filter(order__user = request.user, product = product).first()
            if not user_prev_order or not user_prev_order.order.order_status == 'delivered':
                raise ValidationError({'message': 'you have not purchased product or order is not completed'})
            if rating < 1 or rating > 5:
                raise ValidationError({'message': 'rating must be within the range of 1 - 5'})
            if ProductReview.objects.filter(user = request.user, product = product).exists():
                return Response({"message":'you have already made review on this product' }, status = status.HTTP_422_UNPROCESSABLE_ENTITY)
            try:
                serializer.save()
                return Response({"message":'review added','data':  serializer.data }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
   

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def process_payment(self, request, order):
        # Implement payment processing logic here
        # This is a placeholder function
        return False
    
    def post(self, request, *args, **kwargs):
        cart = get_cart(request.user)
        cart_items = cart.get_cart_items()
        if not cart_items:
            return Response({"message":"cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.create(user=request.user, amount=cart.total_amount(), delivery_address={"address":"some home address"})
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
        if self.process_payment(request, order):
            order.order_status = 'paid'
            order.save()
            cart_items.delete() 
            serializer = OrderSerializer(order)
            return Response( {
                        "message": "Order created successfully",
                        "data": serializer.data }, status=status.HTTP_201_CREATED )
        else :
            order.order_status = 'failed'
            order.save()
            return Response({"message":"payment failed"}, status=status.HTTP_400_BAD_REQUEST)
        
   
class VideoView(mixins.CreateModelMixin, generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = VideoTutorialSerializer
    queryset = VideoTutorial.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        producer = Producer.objects.filter(user_id=request.user.id).first()
        if not producer or producer and not producer.status == 'active':
            raise ValidationError({"message":"producer profile not found or is not active"})
        modified_data = request.data.copy()
        modified_data['producer'] = producer.id
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'data': serializer.data }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
   

class VideoDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): # get single product, update single product
    permission_classes = [IsOwnerOrReadOnly]
    queryset = VideoTutorial.objects.all()
    serializer_class = VideoTutorialSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    

class VideoCommentView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VideoCommentSerializer
    queryset = VideoComment.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = self.kwargs.get('video_id', None)
        if video_id is not None:
            queryset = queryset.filter(video__id=video_id)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy()
        modified_data['user'] = request.user.id
        modified_data['video'] = self.kwargs.get('video_id', None)
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message":'comment added', 'data': serializer.data }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        

class LikedVideoView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LikedVideoSerializer
    queryset = LikedVideo.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = self.kwargs.get('video_id', None)
        if video_id is not None:
            queryset = queryset.filter(video__id=video_id)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy()
        modified_data['user'] = request.user.id
        modified_data['video'] = self.kwargs.get('video_id', None)
        disliked_video = DisLikedVideo.objects.filter(user=request.user, video=modified_data['video'])
        if disliked_video.exists():
            disliked_video.first().delete()
        if LikedVideo.objects.filter(user=request.user, video=modified_data['video']).exists(): 
            LikedVideo.objects.filter(user=request.user, video=modified_data['video']).delete()
            return Response({"message":'you have unliiked this video'}, status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message":'you have liked the video' }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        
class DisLikedVideoView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = DisLikedVideo.objects.all()
    serializer_class = DisLikedVideoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = self.kwargs.get('video_id', None)
        if video_id is not None:
            queryset = queryset.filter(video__id=video_id)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy()
        modified_data['user'] = request.user.id
        modified_data['video'] = self.kwargs.get('video_id', None)
        liked_video = LikedVideo.objects.filter(user=request.user, video=modified_data['video'])
        if liked_video.exists():
            liked_video.first().delete()
        if DisLikedVideo.objects.filter(user=request.user, video=modified_data['video']).exists(): 
            DisLikedVideo.objects.filter(user=request.user, video=modified_data['video']).delete()
            return Response({"message":'you have removed dislike for this video'}, status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message":'you have disliked the video' }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        

class SavedVideoView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SavedVideo.objects.all()
    serializer_class = SavedVideoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        video_id = self.kwargs.get('video_id', None)
        if video_id is not None:
            queryset = queryset.filter(video__id=video_id)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy()
        modified_data['user'] = request.user.id
        modified_data['video'] = self.kwargs.get('video_id', None)
        
        if SavedVideo.objects.filter(user=request.user, video=modified_data['video']).exists(): 
            SavedVideo.objects.filter(user=request.user, video=modified_data['video']).delete()
            return Response({"message":'you have removed saved video'}, status=status.HTTP_204_NO_CONTENT)
        
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message":'you have saved the video' }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FAQView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OrderView(mixins.ListModelMixin,   mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAdminOrSelf]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        
        order  = super().get_queryset()
        if not self.request.user.is_staff:  order = order.filter(user=self.request.user.id) 
        else: order = order.all()
        return order
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
  
  
class OrderDetailView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated ]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
    
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            order = self.get_object()
            if order.user != self.request.user  and not self.request.user.is_staff:
                return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_403_FORBIDDEN)
        return self.retrieve(request, *args, **kwargs)

# cancel order

class CancelOrderView(mixins.ListModelMixin,   mixins.CreateModelMixin, generics.GenericAPIView):  #admin route
    permission_classes = [IsAuthenticated, IsAdminOrSuperuser]

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        if not order.can_be_cancelled():
            return Response({"detail": "Order cannot be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        return Response({"detail": "Order has been cancelled."}, status=status.HTTP_200_OK)


class UserInfo(generics.RetrieveAPIView):
    permission_classes  = [IsAdminOrReadOnly]
    def get_permissions(self):
        if self.request.method in ['GET', 'OPTIONS', 'HEAD']:
            return [AllowAny()]
        return [IsAuthenticated()]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        print("request user is", self.request.user)
        return super().get_queryset()
    def get_object(self):
        return self.request.user
    # def get_object(self):
    

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    

class NotificationView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy()
        modified_data['user'] = request.user.id
        serializer = self.get_serializer(data=modified_data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"message":'notification added', 'data': serializer.data }, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class NotificationDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    generics.GenericAPIView, mixins.DestroyModelMixin): # get single product, update single product
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user, id=self.kwargs['pk'])
        return queryset 
    
    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_opened = True
        notification.save()
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GetWallet(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    
    
    def get_queryset(self):
        return super().get_queryset()
    def get_object(self):
        return Wallet.objects.get(user=self.request.user) #self.request.user
    # def get_object(self):
    

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)





# auth related endpoints
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.username=user.id
        user.first_name=''
        user.last_name=''
        user.set_password(self.request.data['password'])
        user.save()

        # Prepare response data
        self.response_data = {
            "status": "success",
            "message": "Registration successful",
        }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
                token=VerifyEmailToken.objects.create(user=serializer.instance)
                context = {
                        'website_name':"Chowbuddies",
                        "website_domain":"chowbuddies.com",
                        "token_code": token.token,
                        }
                send_email_funct(recipient=serializer.instance.email, template_name='welcome', subject='Verify Your Email', context=context)
                return Response(self.response_data, status=status.HTTP_201_CREATED)
            except Exception as e :
                return Response({"error":f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = [{"field": key, "message": str(value[0])} for key, value in serializer.errors.items()]
            return Response({"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


def verify_email(request, token, email):        
    
    try:
        user=Profile.objects.get(email=email)
        token_record = VerifyEmailToken.objects.get(token=token, user=user)
        if not token_record.token_valid:
            return JsonResponse({"error": "Invalid or expired token."}, status=400)
        user = token_record.user
        user.is_active = True
        user.save()
        token_record.delete()  # Optionally delete the token after verification
        return JsonResponse({"message": "Email verified successfully."})
    except VerifyEmailToken.DoesNotExist:
        return JsonResponse({"error": "Invalid or expired token."}, status=400)
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({'user': {
            'user_id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
        }})
        return data


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            p=Profile.objects.get(email=user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response_data = {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                    "user": {
                        "user_id": str(user.id),
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "isAdmin": user.is_staff,
                        "profileImage":f'{p.profileImage.url}'
                    }
                }
            }
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set the cookie:
            #  - `httponly` prevents JS access
            #  - `secure` ensures it’s only sent over HTTPS in production
            #  - `samesite='Lax'` or `'Strict'` to mitigate CSRF
            response.set_cookie(
                key='accessToken',
                value=access_token,
                httponly=True,
                secure = not settings.DEBUG,
                samesite='Lax',
                max_age=60*60*24,  # e.g. 1 day
            )
            return response

            # return Response(response_data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils import timezone
import logging

# Configure logging for debugging
logger = logging.getLogger(__name__)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                logger.error("Refresh token not provided")
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Blacklist refresh token
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
            logger.info(f"Refresh token blacklisted: {refresh['jti']}")

            # Get access token from Authorization header
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer"):
                logger.warning("No Bearer token found in Authorization header")
                return Response(
                    {"error": "Access token required in Authorization header"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            access_token = auth_header.split(" ")[1]
            # Blacklist access token
            access = AccessToken(access_token)
            outstanding_token = OutstandingToken.objects.create(
                user=request.user,
                jti=access["jti"],
                token=str(access),
                created_at=timezone.now(),
                expires_at=timezone.now(),
            )    
            BlacklistedToken.objects.create(token=outstanding_token, blacklisted_at=timezone.now())
            logger.info(f"Access token blacklisted: {access['jti']}")
            return Response(
                {"status": "success", "message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response(
                {"error": "Invalid token or logout failed"},
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        
# manager endpoints
class AdminLogin(APIView):
    """if user is logged in , check if profile is an admin profile. if so, return token. else reject request"""
    
    def get(self, request, *args, **kwargs):
      #   print(request.user.is_staff or request.user.is_superuser)
      #   return Response({"user":f"{request.user}"}, status=status.HTTP_200_OK)
      pass
    
    
class PublishProduct(APIView):
   permission_classes = [IsAdminOrSuperuser]
   def put(self, request, *args, **kwargs):
         product = request.data.get("product_id")
         if not product :
            return Response({ "field": "product_id", "message": "This field is required."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
         try:
            product = get_object_or_404(Product, id=product)
            if product.is_deleted:
                   return Response({"message":"product is deleted and cannot be updated"}, status=status.HTTP_400_BAD_REQUEST)            
            if not product.status == 'published'and not product.is_deleted:
                product.status = 'published'
                product.save()
                return Response({"message":"product published successfully"}, status=status.HTTP_200_OK)
            return Response(product.data, status=status.HTTP_200_OK)
         except Exception as e :
            return Response({"message":"server cannot be reached"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class DeleteProduct(APIView) :
   permission_classes = [IsAdminOrSuperuser]
   def delete(self, request, *args, **kwargs):
        product = request.data.get("product_id")
        if not product :
            return Response({ "field": "product_id", "message": "This field is required."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            product = get_object_or_404(Product, id=product)
            if not product.is_deleted:
                product.is_deleted = True
                product.save()
                return Response({"message":"product deleted successfully"}, status=status.HTTP_200_OK)
            return Response({"message":"product has already been deleted"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e :
            return Response({"message":"server cannot be reached"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ArchiveProduct(APIView):
   def put(self, request, *args, **kwargs):
        product = request.data.get("product_id")
        if not product :
            return Response({ "field": "product_id", "message": "This field is required."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        try:
            product = get_object_or_404(Product, id=product)
            if not product.is_deleted:
               if not product.status == 'archived':
                  product.status = 'archived'
                  product.save()
                  return Response({"message":"product archived successfully"}, status=status.HTTP_200_OK)
               return Response({"message":"product has already been archived"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message":"product has been deleted"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e :
            return Response({"message":"server cannot be reached"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShipOrderView(mixins.ListModelMixin,   mixins.CreateModelMixin, generics.GenericAPIView):  #admin route
    permission_classes = [IsAdminOrSuperuser]
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
    
    def put(self, request, *args, **kwargs):
        order = self.get_object()
        if not order.payment_status == 'completed':
            raise ValidationError({"message":"order payment must be completed before it can be shipped"})
        try:
            data = bool(request.data['shipped'])
        except KeyError:
            raise ValidationError({"message":"shipped is required (must be boolean)"})
        order.shipped = data
        order.shipped_at = timezone.now() if data else None
        order.order_status = 'shipped' if data else 'pending'
        order.save()
        return Response({"message":"order status updated successfully"}, status=status.HTTP_200_OK)
    
    
class DeliverOrderView(mixins.ListModelMixin,   mixins.CreateModelMixin, generics.GenericAPIView):  #admin route
    permission_classes = [IsAdminOrSuperuser]
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'order_id'
    
    def put(self, request, *args, **kwargs):
        order = self.get_object()
        if not order.shipped:
            raise ValidationError({"message":"order must be shipped before it can be delivered"})
        try:
            data = bool(request.data['delivered'])
        except KeyError:
            raise ValidationError({"message":"delivered is required (must be boolean)"})
        order.delivered = data
        order.delivered_at = timezone.now() if data else None
        
        if data:
            order.order_status = 'delivered' 
        order.save()
        return Response({"message":"order status updated successfully"}, status=status.HTTP_200_OK)
    



def error_404(request, exception=None):
    # print("request path is ", request.path)
    # if "/api" in request.path:
        return JsonResponse(
        {
            "error": "Not Found",
            "detail": "The requested resource was not found on the server. it may have been moved, deleted or never existed."
        },
        status=status.HTTP_404_NOT_FOUND
    )
    # else:
    #     return render("base/")


def error_500(request):
   return JsonResponse(
      {
         "error": "Internal Server Error",
         "detail": "Something went wrong on the server."
      },
      status=status.HTTP_500_INTERNAL_SERVER_ERROR
   )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, WalletTransaction
from .serializers import WalletSerializer, DepositSerializer
import requests
from django.conf import settings

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            response = serializer.save()
            return Response({
                'authorization_url': response['data']['authorization_url'],
                'access_code': response['data']['access_code'],
                'reference': response['data']['reference'],
               
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyPaymentView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({'error': 'Reference is required'}, status=status.HTTP_400_BAD_REQUEST)

        url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
        response = requests.get(url, headers=headers)
        response_data = response.json()
        print("response data is ", response_data)
        if response_data.get('status') and response_data['data']['status'] == 'success':
            transaction = WalletTransaction.objects.get(paystack_payment_reference=reference)
            transaction.status = 'success'
            transaction.save()
            return redirect("http://localhost:3000")
            # return Response({'message': 'Payment verified successfully'}, status=status.HTTP_200_OK)
        elif response_data.get('status') and response_data['data']['status'] == 'failed':
            transaction = WalletTransaction.objects.get(paystack_payment_reference=reference)
            transaction.status = 'failed'
            transaction.save()
            return redirect("http://localhost:3000")
            # return Response({'message': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)


class DepositSerializerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        txns = WalletTransaction.objects.filter(wallet__user__id=request.user.id)
        serializer = DepositSerializer(txns, many=True)
        return Response(serializer.data)


class PaymentMethodView(generics.ListAPIView, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class=PaymentMethodSerializer
    queryset =PaymentMethod.objects.all()
    
    def get(self, request, *args, **kwargs):
        return self.list(self, *args, **kwargs)
    

