import uuid
from channels.generic.websocket import AsyncWebsocketConsumer

GUEST_QUEUE = []
USER_QUEUE = []
ONLINE_USERS = set()  # user_id set


def clean(text: str) -> str:
    return (text or "").replace("|", " ").strip()


def pack_sys(message):
    return f"SYS|{clean(message)}"


def pack_msg(nick, msg):
    return f"MSG|{clean(nick)}|{clean(msg)}"


def pack_match(nick, uid):
    uid = "" if uid is None else str(uid)
    return f"MATCH|{clean(nick)}|{uid}"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        self.room_name = None
        self.partner = None

        session = self.scope["session"]
        user = self.scope["user"]

        self.is_guest = bool(session.get("guest"))
        self.nickname = session.get("guest_nickname") if self.is_guest else session.get("nickname")
        if not self.nickname:
            self.nickname = "Guest"

        self.user_id = user.id if user.is_authenticated else None

        # ✅ Online tracking
        if self.user_id:
            ONLINE_USERS.add(self.user_id)

        # ✅ force reconnect
        force_user_id = session.get("force_match_user_id")
        if force_user_id and self.user_id:
            session["force_match_user_id"] = None
            await self.force_match(force_user_id)
            return

        await self.match()

    async def disconnect(self, close_code):
        if self.is_guest:
            if self in GUEST_QUEUE:
                GUEST_QUEUE.remove(self)
        else:
            if self in USER_QUEUE:
                USER_QUEUE.remove(self)

        if self.user_id and self.user_id in ONLINE_USERS:
            ONLINE_USERS.remove(self.user_id)

        if self.partner:
            await self.partner.send(text_data=pack_sys("Partner disconnected. Click Next."))

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        parts = text_data.split("|", 1)
        cmd = parts[0].upper().strip()

        if cmd == "MSG":
            if not self.room_name:
                return

            msg = parts[1].strip() if len(parts) > 1 else ""
            if not msg:
                return

            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "broadcast_message",
                    "nickname": self.nickname,
                    "message": msg,
                }
            )

        elif cmd == "NEXT":
            # if partner clicked interested but I skip => auto end
            if self.partner:
                await self.partner.send(text_data=pack_sys("Partner skipped. Chat ended."))
            await self.next_match()

        elif cmd == "INTEREST":
            if self.partner:
                await self.partner.send(text_data="PINTEREST|")

    async def match(self):
        # ✅ Guests only match guests
        if self.is_guest:
            if len(GUEST_QUEUE) > 0:
                partner = GUEST_QUEUE.pop(0)
                await self.start_room(partner)
            else:
                GUEST_QUEUE.append(self)
                await self.send(text_data=pack_sys("Waiting for another guest..."))
            return

        # ✅ Logged users only match logged users
        if len(USER_QUEUE) > 0:
            partner = USER_QUEUE.pop(0)
            await self.start_room(partner)
        else:
            USER_QUEUE.append(self)
            await self.send(text_data=pack_sys("Searching for a match..."))

    async def force_match(self, force_id):
        # Only reconnect if other user is online
        if force_id not in ONLINE_USERS:
            await self.send(text_data=pack_sys("User is offline. Reconnect works only when user is online."))
            USER_QUEUE.append(self)
            return

        for partner in list(USER_QUEUE):
            if partner.user_id == force_id:
                USER_QUEUE.remove(partner)
                await self.start_room(partner)
                return

        await self.send(text_data=pack_sys("Reconnect requested... waiting for user..."))
        USER_QUEUE.append(self)

    async def start_room(self, partner):
        self.partner = partner
        partner.partner = self

        room = f"room_{uuid.uuid4().hex[:10]}"
        self.room_name = room
        partner.room_name = room

        await self.channel_layer.group_add(room, self.channel_name)
        await self.channel_layer.group_add(room, partner.channel_name)

        await self.send(text_data=pack_match(partner.nickname, partner.user_id))
        await partner.send(text_data=pack_match(self.nickname, self.user_id))

        await self.channel_layer.group_send(
            room, {"type": "broadcast_system", "message": "✅ Connected! Start chatting."}
        )

    async def next_match(self):
        if self.room_name:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

        if self.partner:
            self.partner.partner = None
            self.partner.room_name = None

        self.partner = None
        self.room_name = None
        await self.match()

    async def broadcast_message(self, event):
        await self.send(text_data=pack_msg(event["nickname"], event["message"]))

    async def broadcast_system(self, event):
        await self.send(text_data=pack_sys(event["message"]))
