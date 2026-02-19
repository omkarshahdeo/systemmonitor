# api.py -  web interface
from fastapi import FastAPI, WebSocket
from monitor import SystemMonitor
from fastapi.responses import HTMLResponse
import asyncio


app = FastAPI()
monitor = SystemMonitor()

@app.get("/metrics")
def get_metrics():
    snapshot = monitor.snapshot()
    return {
        "timestamp": snapshot.timestamp,
        "cpu": {
            "total": snapshot.cpu.total_percent,
            "per_core": snapshot.cpu.per_core
        },
        "memory": {
            "percent": snapshot.memory.percent,
            "swap": snapshot.memory.swap_percent
        },
        "disk": {
            "percent": snapshot.disk.percent
        },
        "network": {
            "upload_per_sec": snapshot.network.upload_per_sec,
            "download_per_sec": snapshot.network.download_per_sec
        },
        "load": snapshot.system.load_avg
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            snapshot = monitor.snapshot()
            await websocket.send_json({
                "cpu": snapshot.cpu.total_percent,
                "memory": snapshot.memory.percent,
                "upload": snapshot.network.upload_per_sec,
                "download": snapshot.network.download_per_sec,
                "load": snapshot.system.load_avg
            })
            await asyncio.sleep(1)
    except:
        await websocket.close()

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get_dashboard():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())