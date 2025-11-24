# System Overlay

A customizable system monitor overlay written in Python using PySide6.
Displays CPU, RAM, and GPU usage.

## Requirements

- Python 3.12+
- PySide6
- psutil

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Configuration

Edit `config.json` to customize the overlay:

- `font_family`: Font name (e.g., "Arial")
- `font_size`: Font size
- `text_color`: Text color (hex)
- `background_color`: Background color (hex)
- `background_opacity`: Background opacity (0.0 - 1.0)
- `update_interval_ms`: Update interval in milliseconds
- `position_x`: X position
- `position_y`: Y position

## GPU Monitoring

GPU monitoring uses `nvidia-smi` if available. If not, it displays 0.0%.
