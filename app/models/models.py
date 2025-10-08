from enum import Enum
from sqlite3.dbapi2 import Timestamp
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Literal

class MessageType(str, Enum):
    TEXT = 'text'
    USER_JOINED = 'user_joined'
    USER_LEFT = 'user_left'
    SYSTEM = 'system'

class ChatMessage(BaseModel):
    message_type : MessageType = MessageType.TEXT
    content : str 
    sender: str 
    room_id : str 
    timestamp: datetime = None 
    recipent: Optional[str] = None

    def __init__(self,**data) -> None:
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.now()
        super().__init__(**data)


class JoinRoomRequest(BaseModel):
    room_id : str 
    username: str 

class CreateRoomRequest(BaseModel):
    room_name: str 
    room_type: Literal['public', 'private'] = 'public'
    creator: str 

class DirectMessageReqeust(BaseModel):
    recepient: str 
    content: str 
    sender: str 

class RoomInfo(BaseModel):
    room_id: str 
    room_name: str 
    room_type: str 
    participants: list[str]
    created_type: datetime
    creator: str 

class UserInfo:
    username: str 
    online: bool
    current_rooms: list[str]

    