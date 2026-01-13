from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from .models import Connection, UserProfile, ReconnectRequest


def landing(request):
    return render(request, "landing.html")


def guest_start(request):
    if request.method == "POST":
        nickname = request.POST.get("nickname", "").strip()
        if not nickname:
            return render(request, "guest.html", {"error": "Nickname is required."})

        # ✅ Fresh guest session
        request.session.flush()
        request.session["guest"] = True
        request.session["guest_nickname"] = nickname[:30]

        return redirect("chat_room")

    return render(request, "guest.html")


def user_register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        email = request.POST.get("email", "").strip()
        custom_id = request.POST.get("custom_id", "").strip()
        password = request.POST.get("password", "")

        if not nickname:
            return render(request, "register.html", {"error": "Nickname is required."})

        if len(password) < 6:
            return render(request, "register.html", {"error": "Password must be at least 6 characters."})

        # ✅ email OR custom_id logic
        if email:
            identity = email
        else:
            if not custom_id or len(custom_id) < 6:
                return render(request, "register.html", {"error": "Custom ID must be 6+ chars if no email."})

            identity = custom_id

        if User.objects.filter(username=identity).exists():
            return render(request, "register.html", {"error": "Account exists. Please login."})

        user = User.objects.create_user(username=identity, password=password, first_name=name)
        user.email = email
        user.save()

        UserProfile.objects.create(user=user, nickname=nickname[:30])

        # ✅ IMPORTANT FIX: clear guest session before login
        if request.session.get("guest"):
            request.session.flush()

        login(request, user)
        request.session["nickname"] = nickname[:30]

        return redirect("chat_room")

    return render(request, "register.html")


def user_login(request):
    if request.method == "POST":
        identity = request.POST.get("identity", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=identity, password=password)
        if not user:
            return render(request, "login.html", {"error": "Invalid credentials."})

        # ✅ IMPORTANT FIX: clear guest session before login
        if request.session.get("guest"):
            request.session.flush()

        login(request, user)

        profile = UserProfile.objects.filter(user=user).first()
        request.session["nickname"] = profile.nickname if profile else "User"

        return redirect("chat_room")

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect("landing")


def chat_room(request):
    # ✅ Guest chat
    if request.session.get("guest"):
        nickname = request.session.get("guest_nickname", "Guest")
        return render(request, "chat.html", {"nickname": nickname, "is_guest": True})

    # ✅ Logged chat
    if request.user.is_authenticated:
        nickname = request.session.get("nickname", "User")
        return render(request, "chat.html", {"nickname": nickname, "is_guest": False})

    return redirect("landing")


@login_required
def connections(request):
    conns = Connection.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "connections.html", {"connections": conns})


@login_required
def save_connection(request):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid method")

    other_user_id = request.POST.get("other_user_id", "").strip()
    other_nickname = request.POST.get("other_nickname", "").strip()

    if not other_user_id or not other_nickname:
        return redirect("chat_room")

    if Connection.objects.filter(owner=request.user).count() >= 10:
        return redirect("connections")

    other_user = User.objects.filter(id=other_user_id).first()
    if not other_user:
        return redirect("chat_room")

    Connection.objects.get_or_create(
        owner=request.user,
        connected_user=other_user,
        defaults={"connected_nickname": other_nickname[:30]},
    )
    return redirect("connections")


@login_required
def send_reconnect_request(request, user_id):
    to_user = User.objects.filter(id=user_id).first()
    if not to_user:
        return redirect("connections")

    ReconnectRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect("connections")


@login_required
def requests_inbox(request):
    inbox = ReconnectRequest.objects.filter(to_user=request.user, is_active=True).order_by("-created_at")
    return render(request, "requests.html", {"requests": inbox})


@login_required
def accept_request(request, req_id):
    req = ReconnectRequest.objects.filter(id=req_id, to_user=request.user, is_active=True).first()
    if not req:
        return redirect("requests_inbox")

    req.is_active = False
    req.save()

    request.session["force_match_user_id"] = req.from_user.id
    return redirect("chat_room")


@login_required
def reject_request(request, req_id):
    req = ReconnectRequest.objects.filter(id=req_id, to_user=request.user, is_active=True).first()
    if req:
        req.is_active = False
        req.save()
    return redirect("requests_inbox")
