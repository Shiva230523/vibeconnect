from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),

    path("guest/", views.guest_start, name="guest_start"),

    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    path("chat/", views.chat_room, name="chat_room"),

    path("connections/", views.connections, name="connections"),
    path("save-connection/", views.save_connection, name="save_connection"),

    path("requests/", views.requests_inbox, name="requests_inbox"),
    path("requests/send/<int:user_id>/", views.send_reconnect_request, name="send_request"),
    path("requests/accept/<int:req_id>/", views.accept_request, name="accept_request"),
    path("requests/reject/<int:req_id>/", views.reject_request, name="reject_request"),
]
