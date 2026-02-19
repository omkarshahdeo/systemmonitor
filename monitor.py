# monitor.py - telemetry engine
import psutil
import time
from dataclasses import dataclass
from typing import List


# ---------- Data Models ----------

@dataclass
class CPUMetrics:
    total_percent: float
    per_core: List[float]


@dataclass
class MemoryMetrics:
    percent: float
    swap_percent: float


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu: float
    memory: float

@dataclass
class NetworkMetrics:
    upload_per_sec: float
    download_per_sec: float

@dataclass
class DiskMetrics:
    total: int
    used: int
    percent: float


@dataclass
class SystemInfo:
    uptime_seconds: float
    load_avg: tuple

@dataclass
class SystemSnapshot:
    timestamp: float
    cpu: CPUMetrics
    memory: MemoryMetrics
    processes: List[ProcessInfo]
    network: NetworkMetrics
    disk: DiskMetrics
    system: SystemInfo

# ---------- Monitor Engine ----------

class SystemMonitor:

    def __init__(self):
        # Prime CPU
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(percpu=True)

        # Initialize network baseline
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()


    def get_cpu(self) -> CPUMetrics:
        return CPUMetrics(
            total_percent=psutil.cpu_percent(interval=None),
            per_core=psutil.cpu_percent(percpu=True)
        )

    def get_memory(self) -> MemoryMetrics:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return MemoryMetrics(
            percent=mem.percent,
            swap_percent=swap.percent
        )


    def get_top_processes(self, limit=10) -> List[ProcessInfo]:
        processes = []

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append(
                    ProcessInfo(
                        pid=proc.pid,
                        name=proc.info['name'] or "unknown",
                        cpu=proc.cpu_percent(interval=None),
                        memory=proc.memory_percent()
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x.cpu, reverse=True)
        return processes[:limit]

    def snapshot(self) -> SystemSnapshot:
        return SystemSnapshot(
            timestamp=time.time(),
            cpu=self.get_cpu(),
            memory=self.get_memory(),
            processes=self.get_top_processes(),
            network=self.get_network(),
            disk=self.get_disk(),
            system=self.get_system_info()
        )
    
    def get_network(self) -> NetworkMetrics:
        current_time = time.time()
        current_net = psutil.net_io_counters()

        elapsed = current_time - self._last_time

        upload = (current_net.bytes_sent - self._last_net.bytes_sent) / elapsed
        download = (current_net.bytes_recv - self._last_net.bytes_recv) / elapsed

        # Update baseline
        self._last_net = current_net
        self._last_time = current_time

        return NetworkMetrics(
            upload_per_sec=upload,
            download_per_sec=download
        )

    def get_disk(self) -> DiskMetrics:
        usage = psutil.disk_usage("/")
        return DiskMetrics(
            total=usage.total,
            used=usage.used,
            percent=usage.percent
        )

    def get_load_average(self):
        try:
            load1, load5, load15 = psutil.getloadavg()
            return (load1, load5, load15)
        except:
            return (0.0, 0.0, 0.0)

    def get_system_info(self) -> SystemInfo:
        uptime = time.time() - psutil.boot_time()
        load = self.get_load_average()
        return SystemInfo(
            uptime_seconds=uptime,
            load_avg=load
        )