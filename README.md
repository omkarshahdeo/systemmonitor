# SystemMonitor

A lightweight system monitor that streams live system metrics to a browser dashboard.

Run one command, open a tab, and watch your machine in real time.

---

## Quick start

Clone the repository and install locally:

```bash
git clone https://github.com/omkarshahdeo/systemmonitor.git
cd systemmonitor

pip install -e .
```

Start the monitor:

```bash
systemmonitor
```

Then open:

```
http://127.0.0.1:8000
```

---

## What it shows

The dashboard displays live metrics for the machine it runs on:

- CPU usage
- Memory usage
- Network throughput
- Load average
- Short-term performance history

Metrics update continuously using WebSocket streaming.

---

## Why this project exists

This project was built to understand how a monitoring system works end-to-end.

Instead of relying on existing monitoring tools, the goal was to build the core pieces from scratch:

- system metrics collection
- real-time streaming
- web dashboard
- CLI launcher
- Python package distribution

---

## Architecture

```
psutil → monitoring engine → FastAPI service
       → WebSocket broadcaster → browser dashboard
```

Metrics are collected once per second and broadcast to connected clients.

---

## Project structure

```
systemmonitor/
│
├── systemmonitor/
│   ├── monitor.py     # system metrics collection
│   ├── api.py         # FastAPI backend
│   ├── cli.py         # command line launcher
│   └── static/        # web dashboard
│
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Future improvements

Possible extensions:

- process monitoring
- alerts for high CPU or memory usage
- longer historical metrics
- configurable refresh intervals
- packaging as a desktop application

---

## License

MIT License
