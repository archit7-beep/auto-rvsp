#!/usr/bin/env python3
import json
import sys
import os
import argparse
import rsvp
from rsvp import fetch_events, send_rsvp, join_group, load_state, save_state, is_seen, mark_seen

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Auto RSVP Bot for Meetup.com")
    parser.add_argument("--config", default="config.json", help="Path to config file (default: config.json)")
    parser.add_argument("--cookie", default="cookie.json", help="Path to cookie file (default: cookie.json)")
    parser.add_argument("--state", help="Path to state file (overrides config)")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending actual RSVPs")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Force execution (disable dry run)")
    parser.set_defaults(dry_run=None) # Default to None to check config
    
    args = parser.parse_args()

    # Load Config
    config = load_json(args.config)
    
    # Load Cookies
    cookie_data = {}
    try:
        cookie_data = load_json(args.cookie)
    except SystemExit:
        # If default fails, check if example exists for helpful error
        if args.cookie == "cookie.json" and not os.path.exists("cookie.json"):
            if os.path.exists("cookie.example.json"):
                 print("\nError: 'cookie.json' not found.")
                 print("Hint: detected 'cookie.example.json'. \n      Run: copy cookie.example.json cookie.json\n      Then edit cookie.json with your actual cookies.")
                 sys.exit(1)
        sys.exit(1)

    cookie_header = cookie_data.get("cookies")
    if not cookie_header:
        print("Error: 'cookies' key missing in cookie file")
        sys.exit(1)

    groups = config.get("groups", [])
    if not groups:
        print("Error: No groups provided in config")
        sys.exit(1)

    # Determine settings
    state_file = args.state if args.state else config.get("state_file", "state.json")
    
    # Dry run
    if args.dry_run is not None:
        dry_run = args.dry_run
    else:
        dry_run = config.get("dry_run", True)

    max_rsvps = config.get("max_rsvps", 1)

    print("Meetup auto RSVP started")
    print(f"Dry run: {dry_run}")
    print(f"State file: {state_file}")

    # Load State
    state = rsvp.load_state(state_file)

    for group in groups:
        rsvp_count = 0
        print(f"\nChecking group: {group}")
        try:
            events = fetch_events(group, cookie_header)
        except Exception as e:
            print(f"Error fetching events for {group}: {e}")
            continue

        for event in events:
            event_id = event["id"]
            title = event["title"]
            rsvp_state = event.get("rsvpState", "UNKNOWN")
            
            if is_seen(event_id, state):
                continue

            print(f"Processing: {title} (State: {rsvp_state})")

            if rsvp_state == "CLOSED" or rsvp_state == "NOT_OPEN_YET":
                print(f"  -> Skipping as RSVP state is {rsvp_state}")
                continue

            if rsvp_state == "JOIN_OPEN":
                if dry_run:
                     print(f"[DRY-RUN] Will join group and RSVP to event {title}")
                else:
                     print(f"State is JOIN_OPEN. Attempting to join group first...")
                     group_id = event.get("groupId")
                     if group_id:
                         if join_group(group_id, cookie_header):
                             print("Successfully joined group!")
                         else:
                             print("Failed to join group. Skipping RSVP.")
                             continue
                     else:
                         print("Could not find group ID. Skipping.")
                         continue

            if dry_run:
                print(f"[DRY-RUN] Would RSVP to: {title} (State: {rsvp_state})")
            else:
                if rsvp_count >= max_rsvps:
                    print(f"Reached max RSVP limit ({max_rsvps}) for this group. Stopping.")
                    break
            
                success = send_rsvp(event_id, cookie_header)

                if success:
                    print(f"RSVP sent for: {title}")
                    rsvp_count += 1
                    mark_seen(event_id, state)
                else:
                    print(f"Failed to RSVP for: {title}")

    # Save state
    rsvp.save_state(state_file, state)
    print("\nDone")

if __name__ == "__main__":
    main()
