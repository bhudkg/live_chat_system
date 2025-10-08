from os import wait
from re import template
from typing import Dict, List
from fastapi import APIRouter, WebSocket, Request
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory='templates')

@router.get("/")
async def home(request: Request):
	return templates.TemplateResponse("general_pages/homepage.html",{"request":request})




@router.get('/router_health', tags=['Health Checks'])
def check_connection():
    return {"message": "Connected."}



websocket_list=[]
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	if websocket not in websocket_list:
		websocket_list.append(websocket)
	while True:
		data = await websocket.receive_text()
		for web in websocket_list:
			if web!=websocket:
				await web.send_text(f"{data}")





# class ConnectionManager:
#     def __init__(self) -> None:
#         self.active_connections : Dict[str, List[WebSocket]] = {}

    

    

