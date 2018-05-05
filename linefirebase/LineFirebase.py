from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
)

from firebase_admin import (
    db
)


class LineFirebase:
    def __init__(self, lineBotApi, firebaseDatabase):
        self.lineBotApi = lineBotApi
        self.db = firebaseDatabase

    def save(self, event):
        print('LineFirebase:', type(event), event)

        if isinstance(event.source, SourceGroup):
            self.saveToGroup(event)
        elif isinstance(event.source, SourceUser):
            self.saveToUser(event)
        elif isinstance(event.source, SourceRoom):
            self.saveToRoom(event)

    def saveToGroup(self, event):
        # Get ref to group
        ref = self.db.reference('/groups')
        ref.child(event.source.group_id).child(event.source.user_id).push(event.as_json_dict())

    def saveToUser(self, event):
        ref = self.db.reference('/users')
        ref.child(event.source.user_id).push(event.as_json_dict())

    def saveToRooms(self, event):
        # Get ref to group
        ref = self.db.reference('/rooms')
        ref.child(event.source.room_id).child(event.source.user_id).push(event.as_json_dict())
