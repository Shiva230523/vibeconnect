from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile, Connection, ReconnectRequest


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "nickname")
    search_fields = ("nickname", "user__username")


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "connected_user", "connected_nickname", "created_at")
    search_fields = ("owner__username", "connected_user__username", "connected_nickname")
    list_filter = ("created_at",)


@admin.register(ReconnectRequest)
class ReconnectRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "from_user", "to_user", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("from_user__username", "to_user__username")
