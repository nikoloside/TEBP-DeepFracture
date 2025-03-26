from fastapi import FastAPI, WebSocket
import requests
import asyncio
import yaml

app = FastAPI()


with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

VULTR_API_KEY = config["vutlr_api_key"]
VULTR_URL = config["vutlr_url"]

# Store WebSocket connections
clients = []

@app.get("/instances")
def get_instances():
    headers = {"Authorization": f"Bearer {VULTR_API_KEY}"}
    response = requests.get(VULTR_URL, headers=headers)
    return response.json()

@app.post("/create_instance")
def create_instance():
    headers = {"Authorization": f"Bearer {VULTR_API_KEY}", "Content-Type": "application/json"}
    data = {
        "region": "ewr",
        "plan": "vc2-1c-1gb",
        "os_id": 387  # Ubuntu 20.04
    }
    response = requests.post(VULTR_URL, headers=headers, json=data)
    return response.json()

@app.delete("/delete_instance/{instance_id}")
def delete_instance(instance_id: str):
    headers = {"Authorization": f"Bearer {VULTR_API_KEY}"}
    response = requests.delete(f"{VULTR_URL}/{instance_id}", headers=headers)
    return {"message": "Instance deleted"}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients:
                await client.send_text(data)
    except:
        clients.remove(websocket)