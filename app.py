# app.py - system monitor app (frontend)

import psutil
import platform

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Vertical, Horizontal

from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from rich.progress import Progress, BarColumn, TextColumn

from monitor import SystemMonitor
from collections import deque
from rich.console import Group

from rich.align import Align
from rich.text import Text


class SystemMonitorApp(App):

    CSS = """
        Screen {
            layout: vertical;
        }

        #cpu, #memory, #network, #disk {
            width: 1fr;
        }

        Horizontal {
            height: auto;
            margin-bottom: 1;
        }
    """


    def __init__(self):
        super().__init__()
        self.monitor = SystemMonitor()
        self.sort_mode = "cpu"
        self.cpu_history = deque(maxlen=60)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("", id="header"),
            Horizontal(
                Static("", id="cpu"),
                Static("", id="memory"),
            ),
            Horizontal(
                Static("", id="network"),
                Static("", id="disk"),
            ),
            Static("", id="processes"),
            Static("", id="footer"),
        )

    async def on_mount(self):
        self.set_interval(1, self.refresh_data)

    def on_key(self, event):
        if event.key == "escape":
            self.exit()
        elif event.key == "m":
            self.sort_mode = "memory"
        elif event.key == "c":
            self.sort_mode = "cpu"

    def refresh_data(self):
        snapshot = self.monitor.snapshot()
        self.cpu_history.append(snapshot.cpu.total_percent)

        def get_color(percent):
            if percent < 50:
                return "green"
            elif percent < 80:
                return "yellow"
            else:
                return "red"

        # ---------- Header ----------
        uptime = int(snapshot.system.uptime_seconds)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60

        load1, load5, load15 = snapshot.system.load_avg

        header_content = Text(
            f"{platform.system()} | "
            f"Uptime: {hours}h {minutes}m | "
            f"Load: {load1:.2f} {load5:.2f} {load15:.2f} | "
            f"Sort: {self.sort_mode.upper()}",
            style="bold"
        )

        self.query_one("#header").update(Align.center(header_content))

        # ---------- CPU ----------
        self.cpu_history.append(snapshot.cpu.total_percent)

        cpu_progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(bar_width=20, complete_style=get_color(snapshot.cpu.total_percent)),
            TextColumn("{task.percentage:>5.1f}%"),
        )

        total_task = cpu_progress.add_task("Total CPU", total=100)
        cpu_progress.update(total_task, completed=snapshot.cpu.total_percent)

        for i, core in enumerate(snapshot.cpu.per_core):
            task = cpu_progress.add_task(f"Core {i}", total=100)
            cpu_progress.update(task, completed=core)

        # Sparkline
        def sparkline(data):
            blocks = "▁▂▃▄▅▆▇█"
            result = ""
            for value in data:
                index = int((value / 100) * (len(blocks) - 1))
                result += blocks[index]
            return result

        history_line = sparkline(self.cpu_history)

        cpu_panel = Panel(
            Group(
                cpu_progress,
                history_line
            ),
            title="CPU"
        )

        self.query_one("#cpu").update(cpu_panel)


        # ---------- Memory ----------
        mem = snapshot.memory

        mem_progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(
                bar_width=20,
                complete_style=get_color(mem.percent)
            ),
            TextColumn("{task.percentage:>5.1f}%"),
        )

        mem_task = mem_progress.add_task("Memory", total=100)
        mem_progress.update(mem_task, completed=mem.percent)

        mem_total = psutil.virtual_memory().total / (1024**3)
        mem_used = psutil.virtual_memory().used / (1024**3)

        swap_percent = mem.swap_percent

        mem_panel = Panel(
            Group(
                mem_progress,
                f"{mem_used:.1f} GB / {mem_total:.1f} GB",
                f"Swap: {swap_percent:.1f}%"
            ),
            title="Memory"
        )


        self.query_one("#memory").update(mem_panel)

        # ---------- Network ----------
        net = snapshot.network

        def format_speed(bytes_per_sec):
            if bytes_per_sec < 1024:
                return f"{bytes_per_sec:.1f} B/s"
            elif bytes_per_sec < 1024**2:
                return f"{bytes_per_sec / 1024:.1f} KB/s"
            else:
                return f"{bytes_per_sec / (1024**2):.1f} MB/s"

        net_text = (
            f"Upload:   {format_speed(net.upload_per_sec)}\n"
            f"Download: {format_speed(net.download_per_sec)}"
        )

        self.query_one("#network").update(Panel(net_text, title="Network"))

        # ---------- Disk ----------
        disk = snapshot.disk

        disk_progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(
                bar_width=20,
                complete_style=get_color(disk.percent)
            ),
            TextColumn("{task.percentage:>5.1f}%"),
        )

        disk_task = disk_progress.add_task("Disk /", total=100)
        disk_progress.update(disk_task, completed=disk.percent)

        disk_total = disk.total / (1024**3)
        disk_used = disk.used / (1024**3)

        disk_panel = Panel(
            Group(
                disk_progress,
                f"{disk_used:.1f} GB / {disk_total:.1f} GB"
            ),
            title="Disk"
        )

        self.query_one("#disk").update(disk_panel)

        # ---------- Processes ----------
        table = Table()
        table.add_column("PID")
        table.add_column("CPU %")
        table.add_column("MEM %")
        table.add_column("Name")

        processes = snapshot.processes

        if self.sort_mode == "memory":
            processes = sorted(processes, key=lambda x: x.memory, reverse=True)
        else:
            processes = sorted(processes, key=lambda x: x.cpu, reverse=True)

        for p in processes:
            table.add_row(
                str(p.pid),
                f"{p.cpu:.1f}",
                f"{p.memory:.1f}",
                p.name
            )

        self.query_one("#processes").update(
            Panel(table, title="Top Processes")
        )

        # ---------- Footer ----------
        footer_text = "m: Sort by Memory   c: Sort by CPU   Esc: Quit"
        self.query_one("#footer").update(footer_text)

if __name__ == "__main__":
    SystemMonitorApp().run()
