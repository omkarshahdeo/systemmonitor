# monitor.py - overall system monitor (backend)
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


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu: float
    memory: float


@dataclass
class SystemSnapshot:
    timestamp: float
    cpu: CPUMetrics
    memory: MemoryMetrics
    processes: List[ProcessInfo]


# ---------- Monitor Engine ----------

class SystemMonitor:

    def __init__(self):
        # Prime CPU measurement (important)
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(percpu=True)
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue


    def get_cpu(self) -> CPUMetrics:
        return CPUMetrics(
            total_percent=psutil.cpu_percent(interval=None),
            per_core=psutil.cpu_percent(percpu=True)
        )

    def get_memory(self) -> MemoryMetrics:
        mem = psutil.virtual_memory()
        return MemoryMetrics(
            percent=mem.percent
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
            processes=self.get_top_processes()
        )