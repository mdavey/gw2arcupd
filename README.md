# gw2arcupd

A command-line utility that can update the `d3d11.dll` file used by ArcDPS for Guild Wars 2.

This is not a serious program.  I just needed a script to download ArcDPS now that I'm on Linux and wanted to play
around with [Textual](https://textual.textualize.io/).

It has only been tested on Linux, and only checks for the Steam version of Guild Wars 2 in the default location.

![Screenshot of the gw2arcupd program](screenshot.png)

## Prerequisites

- Python 3.8+
- uv (or your virtual environment / package manager of choice)

Uses the following python libraries

- Textual
- httpx

## Installation & Usage

```bash
git clone https://github.com/mdavey/gw2arcupd.git
cd gw2arcupd
uv run gw2arcupd
```

## Key Bindings (in the TUI)

| Key | Action | Description                         |
|-----|--------|-------------------------------------|
| `c` | Check  | Check for available updates         |
| `u` | Update | Download and install the latest DLL |
| `d` | Delete | Delete the existing d3d11.dll       |
| `l` | Launch | Run GW2 via Steam                   |
| `q` | Quit   | Exit the application                |


## License

MIT License
