"""
Google Workspace Executive Assistant Tools
==========================================
Handles Google Calendar and Gmail read/create operations.

SETUP REQUIRED (one-time):
1. Go to https://console.cloud.google.com
2. Create a project and enable "Gmail API" and "Google Calendar API"
3. Create OAuth 2.0 credentials → Download as 'credentials.json' into this project root
4. Add GOOGLE_CREDENTIALS_PATH and GOOGLE_TOKEN_PATH to your .env file
5. Run `python app/google_auth.py` once to complete the OAuth consent flow
   and generate `token.json`
"""

import os
import json
import datetime
from langchain_core.tools import tool

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def _get_google_service(service_name: str, version: str):
    """Builds and returns an authenticated Google API service client."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise ValueError(
                    "Google credentials not found or expired. "
                    "Please run `python app/google_auth.py` to authenticate."
                )
            # Save the refreshed token
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())

        return build(service_name, version, credentials=creds)

    except ImportError:
        raise ImportError(
            "Google API libraries are not installed. "
            "Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )


# ─────────────────────────────────────────────
#  GOOGLE CALENDAR TOOLS
# ─────────────────────────────────────────────

@tool
def check_google_calendar(date: str) -> str:
    """
    Retrieves all Google Calendar events for a given date.
    Date format: YYYY-MM-DD (e.g., '2025-06-15').
    Use this when the user asks what's on their schedule, if they have meetings,
    or anything about their calendar for a specific day.
    """
    try:
        service = _get_google_service("calendar", "v3")

        # Build time boundaries for the full day in UTC
        start = datetime.datetime.fromisoformat(date + "T00:00:00")
        end   = datetime.datetime.fromisoformat(date + "T23:59:59")

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        if not events:
            return f"✅ No events found on {date}. Your calendar is clear!"

        lines = [f"📅 Calendar for {date}:"]
        for event in events:
            start_time = event["start"].get("dateTime", event["start"].get("date", "All day"))
            if "T" in start_time:
                # Format datetime string nicely
                dt = datetime.datetime.fromisoformat(start_time.replace("Z", ""))
                start_time = dt.strftime("%I:%M %p")
            summary = event.get("summary", "(No title)")
            lines.append(f"  • {start_time} — {summary}")

        return "\n".join(lines)

    except ValueError as e:
        return f"⚠️ Google Calendar not configured yet: {e}"
    except Exception as e:
        return f"❌ Error fetching calendar: {e}"


@tool
def create_google_calendar_event(
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    description: str = "",
) -> str:
    """
    Creates a new event on the user's Google Calendar.
    Use this when the user asks to block time, schedule something, or set a meeting.
    Parameters:
      - title: Name of the event (e.g., 'Deep Work — AWS Study')
      - date: Date in YYYY-MM-DD format (e.g., '2025-06-15')
      - start_time: Start time in HH:MM 24-hour format (e.g., '09:00')
      - end_time: End time in HH:MM 24-hour format (e.g., '11:00')
      - description: Optional event notes or agenda
    """
    try:
        service = _get_google_service("calendar", "v3")

        start_dt = f"{date}T{start_time}:00"
        end_dt   = f"{date}T{end_time}:00"

        event_body = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_dt, "timeZone": "America/New_York"},
            "end":   {"dateTime": end_dt,   "timeZone": "America/New_York"},
        }

        created_event = service.events().insert(
            calendarId="primary", body=event_body
        ).execute()

        link = created_event.get("htmlLink", "")
        return (
            f"✅ Event created successfully!\n"
            f"  📌 Title: {title}\n"
            f"  📅 Date: {date}\n"
            f"  🕐 Time: {start_time} → {end_time}\n"
            f"  🔗 Link: {link}"
        )

    except ValueError as e:
        return f"⚠️ Google Calendar not configured yet: {e}"
    except Exception as e:
        return f"❌ Error creating event: {e}"


# ─────────────────────────────────────────────
#  GMAIL TOOLS
# ─────────────────────────────────────────────

@tool
def read_recent_emails(max_results: int = 5) -> str:
    """
    Reads the most recent unread emails from the user's Gmail inbox.
    Use this when the user asks 'what emails do I have?', 'check my inbox',
    or 'any important messages?'. Returns sender, subject, and a short snippet.
    """
    try:
        service = _get_google_service("gmail", "v1")

        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=max_results,
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            return "📭 No unread emails in your inbox."

        lines = [f"📬 You have {len(messages)} unread email(s):\n"]
        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()

            headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
            snippet = msg_data.get("snippet", "")[:120]

            lines.append(
                f"📧 From: {headers.get('From', 'Unknown')}\n"
                f"   Subject: {headers.get('Subject', '(No subject)')}\n"
                f"   Date: {headers.get('Date', '')}\n"
                f"   Preview: {snippet}...\n"
            )

        return "\n".join(lines)

    except ValueError as e:
        return f"⚠️ Gmail not configured yet: {e}"
    except Exception as e:
        return f"❌ Error reading emails: {e}"


@tool
def search_gmail(query: str, max_results: int = 5) -> str:
    """
    Searches the user's Gmail for emails matching a query using Gmail search syntax.
    Examples: 'from:boss@company.com', 'subject:invoice', 'AWS receipt'.
    Use this when the user wants to find a specific email or thread.
    """
    try:
        service = _get_google_service("gmail", "v1")

        results = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            return f"📭 No emails found matching: '{query}'"

        lines = [f"🔍 Gmail results for '{query}':\n"]
        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()

            headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
            snippet = msg_data.get("snippet", "")[:120]

            lines.append(
                f"📧 From: {headers.get('From', 'Unknown')}\n"
                f"   Subject: {headers.get('Subject', '(No subject)')}\n"
                f"   Date: {headers.get('Date', '')}\n"
                f"   Preview: {snippet}...\n"
            )

        return "\n".join(lines)

    except ValueError as e:
        return f"⚠️ Gmail not configured yet: {e}"
    except Exception as e:
        return f"❌ Error searching Gmail: {e}"
