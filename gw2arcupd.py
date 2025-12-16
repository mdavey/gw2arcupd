#!/usr/bin/env -S uv run

import hashlib
import subprocess
from pathlib import Path

import httpx
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Log

DLL_URL = "https://www.deltaconnected.com/arcdps/x64/d3d11.dll"
MD5_URL = "https://www.deltaconnected.com/arcdps/x64/d3d11.dll.md5sum"
RUN_COMMAND = ["steam", "steam://rungameid/1284210"]

def get_gw2_path() -> Path | None:
    if (Path.home() / ".steam" / "steam" / "steamapps" / "common" / "Guild Wars 2").exists():
        return Path.home() / ".steam" / "steam" / "steamapps" / "common" / "Guild Wars 2"
    return None

def compute_md5(file_path: Path) -> str | None:
    try:
        data = file_path.read_bytes()
        return hashlib.md5(data).hexdigest()
    except FileNotFoundError:
        return None

async def fetch_text(url: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text.strip()

async def fetch_md5_remote() -> str:
    txt = await fetch_text(MD5_URL)
    return txt.split()[0]

async def check_update_needed() -> bool|None:
    gw2_path = get_gw2_path()
    if not gw2_path:
        return None
    dll_path = gw2_path / "d3d11.dll"
    local_md5 = compute_md5(dll_path)
    remote_md5 = await fetch_md5_remote()
    if not remote_md5:
        return None
    if local_md5 != remote_md5:
        return True
    return False

async def download_dll() -> None:
    gw2_path = get_gw2_path()
    if not gw2_path:
        raise FileNotFoundError("GW2 directory not found")
    dll_path = gw2_path / "d3d11.dll"
    async with httpx.AsyncClient() as client:
        resp = await client.get(DLL_URL)
        resp.raise_for_status()
        dll_path.write_bytes(resp.content)

class Gw2UpdApp(App):
    # CSS_PATH = "gw2upd.css"
    BINDINGS = [
        ("c", "check_for_update()", "Check"),
        ("u", "update()", "Update"),
        ("d", "disable()", "Delete"),
        ("l", "launch()", "Launch"),
        ("q", "quit()", "Quit"),
    ]

    CSS = """
    Log {
        margin: 1 2 0 2;
    }
    
    .log_container {
        height: auto;
    }
    
    .button_container {
        height: auto;
        align: center bottom;
    }
    
    Button {
        margin: 1 2;
    }
    """

    logger = Log()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

        # self.logger.styles.margin = (1, 2)
        yield Vertical(
            self.logger,
            Horizontal(
                # No idea why action="stuff" here doesn't work.
                Button("Check (C)", id="check"),
                Button("Update (U)", id="update"),
                Button("Delete (D)", id="disable"),
                Button("Launch GW2 (L)", id="launch"),
                Button("Quit (Q)", id="quit"),
                classes="button_container"
            ),
            classes="log_container"
        )

    async def on_mount(self) -> None:
        self.title = "ArcDPS Updater"
        self.sub_title = "v0.02"
        self.theme = "nord"

        path = get_gw2_path()
        if path:
            self.log_message(f"Found GW2 directory @ {path}")
        else:
            self.log_message("Unable to find GW2 directory")

    async def on_button_pressed(self, event):
        if event.button.id == "update":
            await self.action_update()
        elif event.button.id == "disable":
            await self.action_disable()
        elif event.button.id == "check":
            await self.action_check_for_update()
        elif event.button.id == "quit":
            await self.action_quit()
        elif event.button.id == "launch":
            await self.action_launch()

    async def action_update(self):
        if not get_gw2_path():
            self.log_message("GW2 directory not found")
            return

        self.log_message("Downloading latest version...")
        try:
            await download_dll()
            self.log_message("Updated successfully")
        except Exception as e:
            self.log_message(f"Error: {e}")

    async def action_disable(self):
        gw2_path = get_gw2_path()
        if not gw2_path:
            self.log_message("GW2 directory not found")
            return

        dll_path = gw2_path / "d3d11.dll"
        if not dll_path.is_file():
            self.log_message("d3d11.dll not found, nothing to delete")
            return

        try:
            dll_path.unlink()
            self.log_message("Removing existing d3d11.dll")
        except FileNotFoundError:
            self.log_message("Failed to remove d3d11.dll: Already absent")

    async def action_check_for_update(self):
        if not get_gw2_path():
            self.log_message("GW2 directory not found")
            return

        need_update = await check_update_needed()

        if need_update is None:
            self.log_message(f"Error, checking for update")
        elif need_update:
            self.log_message(f"Update available")
        else:
            self.log_message(f"No update available, latest version already installed")

    async def action_launch(self):
        subprocess.run(RUN_COMMAND)

    def log_message(self, message: str) -> None:
        """Write a message to the Log widget."""
        self.logger.write_line(message, True)


if __name__ == "__main__":
    Gw2UpdApp().run()