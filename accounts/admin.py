from django.contrib import admin
from .models import Profile, PasswordResetRequest, VerifyEmailToken, Producer, ShippingInfo
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib import messages


class ProfileAdmin(UserAdmin):
    model = Profile
    list_display = [ 'email', 'id', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login', 'is_active', "profileImage",
                    'is_currently_logged_in', 'logged_in_devices']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ( 'default_shipping_address', 'connected_devices', "profileImage")}),
    )
    actions = ['logout_user', 'toggle_active_status']

    def logout_user(self, request, queryset):
        """
        Logs out the selected user by deleting their active sessions.
        """
        for user in queryset:
            # Find active sessions for the user and delete them
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            count = 0
            for session in sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(user.id):
                    session.delete()
                    count += 1
            if count > 0:
                self.message_user(request, f'{count} session(s) logged out for user {user}.')
            else:
                self.message_user(request, f'No active sessions found for user {user}.', level=messages.WARNING)
                
    logout_user.short_description = "Log out selected users"

    def toggle_active_status(self, request, queryset):
        """
        Toggles the is_active status for the selected users.
        """
        for user in queryset:
            user.is_active = not user.is_active  # Toggle the is_active status
            user.save()

            status = 'activated' if user.is_active else 'deactivated'
            self.message_user(request, f'User {user.email} has been {status}.')

    def is_currently_logged_in(self, obj):
        """
        Check if the user is currently logged in by verifying if they have any active session.
        """
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in active_sessions:
            data = session.get_decoded()
            if str(obj.id) == data.get('_auth_user_id'):
                return True
        return False
    
    def logged_in_devices(self, obj):
        """
        Return the number of devices the user is logged in on by counting their active sessions.
        """
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        count = 0
        for session in active_sessions:
            data = session.get_decoded()
            if str(obj.id) == data.get('_auth_user_id'):
                count += 1
        return count
    
    is_currently_logged_in.short_description = "Currently Logged In"
    is_currently_logged_in.boolean = True
    toggle_active_status.short_description = "Toggle active status of selected users"
    logged_in_devices.short_description = "Logged In Devices"


class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ['email', 'token', 'created_at', 'used']


class VerifyEmailTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Producer)
admin.site.register(ShippingInfo)
admin.site.register(PasswordResetRequest, PasswordResetRequestAdmin)
admin.site.register(VerifyEmailToken, VerifyEmailTokenAdmin)

