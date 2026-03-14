from pathlib import Path

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# api.py -  web interface
from fastapi import FastAPI, WebSocket
from systemmonitor.monitor import SystemMonitor
from fastapi.responses import HTMLResponse
import asyncio
import os
import logging

last_snapshot_time = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REFRESH_INTERVAL = float(os.getenv("REFRESH_INTERVAL", 1))

app = FastAPI()
monitor = SystemMonitor()
clients = set()
history = []
MAX_HISTORY = 300

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
    clients.add(websocket)

    try:
        while True:
            await asyncio.sleep(REFRESH_INTERVAL)

    except:
        clients.remove(websocket)


from fastapi.staticfiles import StaticFiles
from pathlib import Path
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


from fastapi.responses import FileResponse

@app.get("/")
def root():
    return FileResponse(STATIC_DIR / "index.html")


@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(snapshot_loop())


@app.get("/history")
def get_history():
    return history


async def snapshot_loop():
    global history, last_snapshot_time

    while True:
        try: 
            snapshot = monitor.snapshot()

            data = {
                "timestamp": snapshot.timestamp,
                "cpu": {
                    "total": snapshot.cpu.total_percent
                },
                "memory": {
                    "percent": snapshot.memory.percent
                },
                "network": {
                    "upload": snapshot.network.upload_per_sec,
                    "download": snapshot.network.download_per_sec
                },
                "load": snapshot.system.load_avg
            }

            # ---- Store history ----
            history.append(data)
            if len(history) > MAX_HISTORY:
                history.pop(0)

            # ---- Broadcast safely ----
            for client in clients.copy():
                try:
                    await client.send_json(data)
                except:
                    clients.remove(client)

            await asyncio.sleep(1)
            logger.info("Snapshot broadcasted to %d clients", len(clients))
            global last_snapshot_time
            last_snapshot_time = snapshot.timestamp
        
        except Exception as e: 
            logger.error("Snapshot loop error: %s",e)

        await asyncio.sleep(REFRESH_INTERVAL)

@app.get("/health")
def health():
    if last_snapshot_time is None:
        return {"status": "starting"}

    age = time.time() - last_snapshot_time
    if age > REFRESH_INTERVAL * 3:
        return {"status": "stale"}
    
    return {"status": "ok"}

@app.on_event("shutdown")
def shutdown_event():
    logger.info("SystemMonitor shutting down cleanly.")