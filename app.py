# app.py

from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Vertical
from rich.table import Table
from rich.panel import Panel
from monitor import SystemMonitor


class SystemMonitorApp(App):

    CSS = """
    Screen {
        layout: vertical;
    }
    """

    def __init__(self):
        super().__init__()
        self.monitor = SystemMonitor()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(id="cpu"),
            Static(id="memory"),
            Static(id="processes"),
        )

    async def on_mount(self):
        self.set_interval(1, self.refresh_data)

    def refresh_data(self):
        snapshot = self.monitor.snapshot()

        # CPU Section
        cpu_text = f"Total CPU: {snapshot.cpu.total_percent:.1f}%\n"
        cpu_text += "Per Core: " + ", ".join(
            f"{core:.1f}%" for core in snapshot.cpu.per_core
        )
        self.query_one("#cpu").update(Panel(cpu_text, title="CPU"))

        # Memory Section
        mem_text = f"Memory Usage: {snapshot.memory.percent:.1f}%"
        self.query_one("#memory").update(Panel(mem_text, title="Memory"))

        # Process Table
        table = Table()
        table.add_column("PID")
        table.add_column("CPU %")
        table.add_column("MEM %")
        table.add_column("Name")

        for p in snapshot.processes:
            table.add_row(
                str(p.pid),
                f"{p.cpu:.1f}",
                f"{p.memory:.1f}",
                p.name
            )

        self.query_one("#processes").update(
            Panel(table, title="Top Processes")
        )


if __name__ == "__main__":
    SystemMonitorApp().run()
