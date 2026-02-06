# Meetup Auto RSVP

A cross-platform Python tool that helps you stay on top of upcoming Meetup.com events for your favorite groups.

## Features

- **Event Detection**: Checks for upcoming events by interacting with Meetup functionality.
- **Assists with RSVP**: Attempts to RSVP to events based on your configuration.
- **Auto-Join Assistance**: Can attempt to join a group if membership is required for an event.
- **Multi-Group Processing**: Cycles through your configured list of groups.
- **Smart Logic**:
    - Detects whether an event is open for RSVP.
    - Can retry on subsequent runs if an attempt was not successful.
- **CLI & Linux Compatible**: Designed to run via command line on Windows, Linux, and macOS.

## Limitations

> [!IMPORTANT]
> **This tool relies on internal Meetup APIs which are not public.** 
> Functionality is **best-effort** and may break if Meetup changes their platform. 
> Always verify important RSVPs manually on the Meetup website or app.

## Installation

1.  **Clone or Download** this repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Quick Start

1.  **Setup Configuration**:
    Follow the detailed instructions in [SETUP.md](SETUP.md) to obtain your session cookie and configure `config.json`.

2.  **Run the Script**:
    ```bash
    python main.py
    ```

## CLI Usage

The script supports command-line arguments for easier management:

```bash
# Run in Dry-Run mode (check events without RSVPing)
python main.py --dry-run

# Force execution (override config setting)
python main.py --no-dry-run

# Use a specific config file
python main.py --config my_config.json

# View all options
python main.py --help
```

## Files

- `main.py`: The entry point script.
- `rsvp.py`: Components for interacting with Meetup.
- `config.json`: Stores your group list and settings.
- `cookie.json`: Stores your session cookie.
- `state.json`: Tracks processed events to avoid duplicates.
