# Setup Guide for Meetup Auto RSVP

To use this tool with your own Meetup account, you need to provide your **Login Cookie** and **Group List**.

## 1. Get Your Cookie

The script interacts with Meetup by using your existing browser session.

> [!CAUTION]
> **Security Warning**: Your session cookie gives full access to your Meetup account. 
> *   **NEVER share your `cookie.json` file.**
> *   **NEVER paste your cookie into public forums or chats.**
> *   Treat this file like your password.

1.  **Login**: Open [Meetup.com](https://www.meetup.com) in Chrome or Firefox and log in.
2.  **Open Developer Tools**: Press `F12` (or Right Click > Inspect).
3.  **Go to Network Tab**: Click on the "Network" tab in the developer tools.
4.  **Refresh**: Refresh the page. You will see many requests appear.
5.  **Find a Request**: Click on the request named `events/` or `gql2` (you can filter by "gql2").
6.  **Copy Cookie**:
    *   Click on the found request.
    *   Scroll down to the **Request Headers** section.
    *   Find the `Cookie` header.
    *   Right-click the value and **Copy Value**. It will be a long string starting with `MEETUP_MEMBER` or similar.

## 2. Configure `cookie.json`

Create a file named `cookie.json` in the project folder (if it doesn't exist) and paste your cookie string:

```json
{
  "cookies": "PASTE_YOUR_HUGE_COOKIE_STRING_HERE"
}
```

> **Note**: If you log out of Meetup in your browser, these cookies might expire. If usage fails, repeat these steps to get a fresh cookie.

## 3. Configure Groups (`config.json`)

Open `config.json` and add the groups you want to check. The group name is the **slug** found in the URL.

*   **Example URL**: `https://www.meetup.com/my-cool-group/`
*   **Group Slug**: `my-cool-group`

Edit `config.json` like this:

```json
{
  "groups": [
    "my-cool-group",
    "another-tech-group"
  ],
  "check_interval_minutes": 60,
  "dry_run": false,
  "max_rsvps": 1,
  "state_file": "state.json"
}
```

### Configuration Options:
*   **`groups`**: List of group slugs to retrieve events for.
*   **`dry_run`**: Set to `true` to test without sending RSVPs. Set to `false` (or use `--no-dry-run` CLI flag) to enable active attempts.
*   **`max_rsvps`**: The maximum number of events to process *per group* in a single run.
*   **`state_file`**: File to store the history of seen events (default: `state.json`).

## 4. Run the Tool

**Windows**:
```powershell
python main.py
```

**Linux/Mac**:
```bash
chmod +x main.py
./main.py
```

## Troubleshooting

### HTTP 404 / 401 Errors
Your cookies are likely invalid, expired, or copied incorrectly.
*   Solution: Log out and log back in on your browser, then grab a fresh cookie string.

### "Failed to join group"
The tool assists with auto-joining groups if the event requires it, but this logic is not guaranteed.
*   Ensure your account didn't hit the max group limit on Meetup.
*   Ensure you are not blocked from that specific group.

### Script runs but does not RSVP
*   Check if `dry_run` is set to `true` in `config.json` (logs will say `[DRY-RUN]`).
*   Check if you already RSVP'd (logs will say `State: YES` or `State: RSVP`).
*   Check if events are closed (logs will say `Skipping as RSVP state is CLOSED`).
