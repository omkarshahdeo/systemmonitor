import uvicorn
import webbrowser
import threading
from systemmonitor.api import app

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

def main():
    print("Starting SystemMonitor at http://127.0.0.1:8000")

    threading.Timer(1.0, open_browser).start()

    uvicorn.run(app, host="127.0.0.1", port=8000)
