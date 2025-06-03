from base.models import Cart, CartItem, Order, OrderItem, UserLog


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
        
    