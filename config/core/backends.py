from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class IINOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        if '+' in username:
            try:
                user = User.objects.get(phone=username)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(iin=username)
            except User.DoesNotExist:
                return None
        if user.check_password(password):
            return user
        return None