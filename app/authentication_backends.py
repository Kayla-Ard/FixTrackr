from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        logger.info(f"Attempting to authenticate user with email: {username}")
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            logger.error(f"User with email {username} does not exist.")
            return None
        if user.check_password(password):
            logger.info(f"Authentication successful for user: {username}")
            return user
        else:
            logger.error(f"Authentication failed for user: {username}")
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist.")
            return None
