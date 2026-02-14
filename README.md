Terminal System Monitor (Textual + Rich + psutil)

A terminal-based real-time system monitor built using Python, Textual, Rich, and psutil. Features structured telemetry, interactive process sorting, and time-series CPU visualization.

Features: 
   1. CPU (total + per-core + sparkline)
   2. Load average
   3. Memory + swap
   4. Disk usage
   5. Network throughput
   6. Interactive process sorting
   7. Real-time refresh loop

Architecture: 
   monitor.py → telemetry engine
   app.py     → reactive UI layer

Tech Stack: 
   Python 3.x
   psutil
   textual
   rich

Future Improvements: 
   Process filtering
   Kill process feature
   Network history
   Configurable refresh rate
   Theming