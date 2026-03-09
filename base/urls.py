
from django.urls import path #type: ignore
from . import views
from drf_yasg.views import get_schema_view 
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from django.urls import path
from .views import WalletView, DepositView, VerifyPaymentView

schema_view = get_schema_view(
    openapi.Info( 
        title="Chowbuddies API",
        default_version='v1',
        description="Chowbuddies API documentation guide",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="uwayasidney@gmail.com"), 
        license=openapi.License(name="Proprietary  License"), 
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', views.HomePage.as_view()), 
    path('profiles/', views.ProfileView.as_view()),
    path('profiles/<id>/', views.ProfileDetailView.as_view()),
    path('profiles/<id>/<transactions>', views.UserTxnsView.as_view()),
    path("user/", views.UserInfo.as_view()),
    path("orders/", views.OrderView.as_view(), ),
    path("orders/<order_id>/", views.OrderDetailView.as_view(), ),
    path("orders/<order_id>/ship/", views.ShipOrderView.as_view(), ),
    path("orders/<order_id>/deliver/", views.DeliverOrderView.as_view(), ),
    path('products/', views.ProductView.as_view()),
    path('products/<uuid:prod_id>/', views.ProductDetailView.as_view()),
    path('products/<uuid:product_id>/reviews/', views.ProductReviewView.as_view()),
    path('categories/', views.ProductCategoryView.as_view()),
    path('categories/<int:pk>/', views.ProductCategoryDetailView.as_view()),
    path('cart/', views.CartView.as_view()),
    path('cart/<int:pk>/', views.CartDetailView.as_view()),
    path("checkout/", views.CheckoutView.as_view()),
    path('videos/', views.VideoView.as_view()),
    path('videos/<int:id>/', views.VideoDetailView.as_view()),
    path('videos/<int:video_id>/comments/', views.VideoCommentView.as_view()),
    path('videos/<int:video_id>/likes/', views.LikedVideoView.as_view()),
    path('videos/<int:video_id>/dislikes/', views.DisLikedVideoView.as_view()),
    path('videos/<int:video_id>/saved/', views.SavedVideoView.as_view()),
    path('faq/' , views.FAQView.as_view()),
    path('auth/signup/', views.RegisterView.as_view(), name='register'),
    path('auth/signin/', views.LoginView.as_view(), name='login'),
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('manager/', views.AdminLogin.as_view()),
    path( 'manager/products/approve/', views.PublishProduct.as_view() ),
    path( 'manager/products/delete/', views.DeleteProduct.as_view() ),
    path( 'manager/products/archive/', views.ArchiveProduct.as_view() ),
    path("notifications/", views.NotificationView.as_view()),
    path("notifications/<int:pk>/", views.NotificationDetailView.as_view()),
  
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    

    path('wallet/', WalletView.as_view(), name='wallet'),
    path('wallet-dep/', views.DepositSerializerView.as_view()),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify_payment'),
    
    path('methods', views.PaymentMethodView.as_view()),
    
    path('verify/<str:token>/<str:email>/', views.verify_email, name='verify_email'),
    
]