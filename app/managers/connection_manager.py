


from ast import Dict
from email import message
import imp
from math import log
from sre_compile import dis
import webbrowser
from fastapi import WebSocket
from typing import List, Dict, Set

from pydantic import root_model
from models.models import ChatMessage, MessageType, RoomInfo
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ConectionManager:
    def __init__(self) -> None:

        #connections in a room
        self.room_connections: Dict[str, List[WebSocket]] = {}

        #direct connection
        self.user_connections: Dict[str, WebSocket] = {}

        #user_to_rooms_included
        self.user_rooms: Dict[str, Set[WebSocket]] = {}

        #room_info_storage
        self.rooms: Dict[str, RoomInfo] = {}

        self.active_users: Set[str] = Set()

    async def connect_to_room(self, room_id: str, username: str, websocket: WebSocket):
        try:
            await websocket.accept()

            if room_id not in self.room_connections:
                self.room_connections[room_id] = []

            if room_id not in self.rooms:
                self.rooms[room_id] = RoomInfo(
                    room_id=room_id,
                    room_name=f"room: {room_id}",
                    room_type='public',
                    participants=[],
                    created_type=datetime.now(),
                    creator=username
                )
            self.user_connections[username] = websocket

            self.room_connections[room_id].append(websocket)

            if username not in self.user_rooms:
                self.user_rooms[username] = set()
        
            self.user_rooms[username].add(room_id)

            if username not in self.rooms[room_id].participants:
                self.rooms[room_id].participants.append(username)

            join_message = ChatMessage(
                message_type=MessageType.USER_JOINED,
                room_id = room_id,
                sender = username,
                content = f"{username} joined."
            )

            #broadcast this message in room
            self.broadcast_to_room(join_message, room_id)

            logger.info(f"{username} joined the room: {room_id}")
            return True
        except Exception as e:
            print(e)

    
    async def disconnect_from_room(self, websocket: WebSocket, username: str, room_id: str):
        try:
            if room_id in self.room_connections:
                if websocket in self.room_connections[room_id]:
                    self.room_connections[room_id].remove(websocket)

                if not self.room_connections[room_id]:
                    del self.room_connections[room_id]

            if username in self.user_connections:
                del self.user_connections[username]

            if  username in self.user_rooms  and room_id in self.user_rooms[username]:
                self.user_rooms[username].remove(room_id)
                if not self.user_rooms[room_id]:
                    del self.user_rooms[room_id]

            if room_id in self.rooms and username in self.rooms[room_id].participants:
                self.rooms[room_id].participants.remove(username)

            if username not in self.user_rooms:
                self.active_users.discard(username)

            if room_id in self.room_connections:
                leave_message = ChatMessage(
                    message_type = MessageType.USER_LEFT,
                    content = f"{username} left",
                    sender = "System",
                    room_id = room_id,
                )

                self.broadcast_to_room(leave_message, room_id)
                logger.info(f"User {username} disconnected from room {room_id}")
            return True

        except Exception as e:
            print(e)


    async def broadcast_to_room(self, message: ChatMessage, room_id: str):
        if room_id not in self.room_connections:
            return 

        try:
            message_dict = message.model_dump()
            message_dict['timestamp'] = message.timestamp.isoformat()

            disconnected_devices = []

            for conn in self.room_connections[room_id]:
                try:
                    await conn.send_text(json.jump(message_dict))
                except Exception as e:
                    logger.error(f"Error of sending data for {conn}, Error: {e}")
                    disconnected_devices.append(conn)

            for disconnected_device in disconnected_devices:
                self.room_connections[room_id].remove(disconnected_device)
        except Exception as e:
            logger.error(f"Error {e}")


    async def send_direct_message(self, message: ChatMessage):
        """ Send direct message """
        if not message.recipent or message.recipent not in self.user_connections:
            logger.error(f"Can not send this message as user not in connection list")
            return False

        message_dict = message.model_dump()
        message_dict['timestamp'] = message.timestamp.isoformat()

        
        

