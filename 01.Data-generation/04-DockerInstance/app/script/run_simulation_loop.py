import subprocess
import os
import asyncio
import websockets

async def send_log_to_dashboard(log_message):
    uri = "ws://localhost:8000/ws/logs"
    async with websockets.connect(uri) as websocket:
        await websocket.send(log_message)

def run_init_drive_google():
    subprocess.run(["python3", "04-Docker/init_drive_google.py"], check=True)

def run_simulation_script():
    # Replace this with the actual simulation script command
    subprocess.run(["python3", "path/to/simulation_script.py"], check=True)

async def main_loop():
    run_init_drive_google()
    while True:
        run_simulation_script()
        log_message = "Simulation loop completed successfully."
        await send_log_to_dashboard(log_message)
        await asyncio.sleep(1)  # Adjust the sleep time as needed

if __name__ == "__main__":
    asyncio.run(main_loop())
