from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=30)

    def __str__(self):
        return self.nickname


class Connection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connections")
    connected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connected_to")
    connected_nickname = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "connected_user")


class ReconnectRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
