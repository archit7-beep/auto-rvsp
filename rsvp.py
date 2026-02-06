import json
import requests
import os
import re
from bs4 import BeautifulSoup


# ---------------- STATE HANDLING ----------------

def load_state(state_file):
    if not os.path.exists(state_file):
        return {"seen_events": []}

    with open(state_file, "r") as f:
        return json.load(f)


def save_state(state_file, state):
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def is_seen(event_id, state):
    return event_id in state.get("seen_events", [])


def mark_seen(event_id, state):
    state.setdefault("seen_events", []).append(event_id)


# ---------------- FETCH EVENTS ----------------

def fetch_events(group, cookie_header):
    url = f"https://www.meetup.com/{group}/events/"

    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")

    if not script:
        return []

    data = json.loads(script.string)
    apollo = data.get("props", {}).get("pageProps", {}).get("__APOLLO_STATE__", {})

    events = []

    for key, value in apollo.items():
        if key.startswith("Event:"):
            if value.get("status") != "ACTIVE":
                continue

            events.append({
                "id": value.get("id"),
                "title": value.get("title"),
                "url": value.get("eventUrl"),
                "rsvpState": value.get("rsvpState"),
                "groupId": value.get("group", {}).get("__ref", "").replace("Group:", "")
            })

    return events

# ---------------- RSVP ACTION ----------------

def send_rsvp(event_id, cookie_header):
    """
    Attempts to RSVP to a Meetup event using GraphQL.
    Returns True if request succeeded, False otherwise.
    """
    
    # Endpoint identified on 2026-01-28
    url = "https://www.meetup.com/gql2"

    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.meetup.com"
    }

    # Mutation: rsvp(input) -> RsvpPayload
    query = """
    mutation { 
        rsvp(input: { eventId: "%s", response: YES }) { 
            __typename 
        } 
    }
    """ % event_id

    payload = {
        "query": query
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Check for GraphQL errors
            if "errors" in data:
                print(f"GraphQL Error: {data['errors'][0].get('message')}")
                return False
            return True
        else:
            print(f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception sending RSVP: {e}")
        return False


# ---------------- JOIN GROUP ----------------

def join_group(group_id, cookie_header):
    """
    Attempts to join a Meetup group using GraphQL.
    Returns True if request succeeded, False otherwise.
    """
    url = "https://www.meetup.com/gql2"
    
    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://www.meetup.com"
    }

    # Mutation: joinGroup(input)
    query = """
    mutation { 
        joinGroup(input: { groupId: "%s" }) { 
            __typename
        } 
    }
    """ % group_id

    payload = { "query": query }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"GraphQL Error joining group: {data['errors'][0].get('message')}")
                return False
            return True
        else:
            print(f"HTTP Error joining group: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception joining group: {e}")
        return False
