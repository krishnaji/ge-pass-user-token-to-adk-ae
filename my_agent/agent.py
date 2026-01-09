import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
import json
import logging
import sys
# for using the token to retrieve the email
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build	
from google.adk.agents.readonly_context import ReadonlyContext
DEBUG_CONTEXT = (
    os.getenv("DEBUG_CONTEXT", "true").lower() == "true"
)  # Set to false to disable debug logging

MIN_TOKEN_LENGTH = 20
def get_email_from_token(access_token):
    """Get user info from access token"""
    credentials = Credentials(token=access_token)
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    user_email = user_info.get('email')
    
    return user_email

def lazy_mask_token(access_token):
    """Mask access token for printing"""
    start_mask = access_token[:4]
    end_mask = access_token[-4:]
    
    return f"{start_mask}...{end_mask}"
def debug_print_context(readonly_context: ReadonlyContext):
    """Print ALL context and session data for debugging."""
    if not DEBUG_CONTEXT:
        return
    import json

    def safe_serialize(obj, depth=0):
        """Recursively serialize object to JSON-compatible format."""
        if depth > 10:
            return f"<max depth reached: {type(obj).__name__}>"
        try:
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            if isinstance(obj, dict):
                return {str(k): safe_serialize(v, depth + 1) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [safe_serialize(item, depth + 1) for item in obj]
            if hasattr(obj, "__dict__"):
                return {
                    "_type": type(obj).__name__,
                    **{
                        k: safe_serialize(v, depth + 1) for k, v in obj.__dict__.items()
                    },
                }
            if hasattr(obj, "items"):
                return {str(k): safe_serialize(v, depth + 1) for k, v in obj.items()}
            return str(obj)
        except Exception as e:
            return f"<error: {type(e).__name__}: {e}>"

    print("=" * 80, file=sys.stderr)
    print("DEBUG: FULL CONTEXT AND SESSION STATE DUMP", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    # 1. Print all attributes of readonly_context (including private ones)
    print("\n--- readonly_context ALL attributes ---", file=sys.stderr)
    for attr in dir(readonly_context):
        try:
            value = getattr(readonly_context, attr)
            if not callable(value):
                print(f"  {attr}: {safe_serialize(value)}", file=sys.stderr)
        except Exception as e:
            print(f"  {attr}: <error accessing: {e}>", file=sys.stderr)

    # 2. Print readonly_context.__dict__ directly
    print("\n--- readonly_context.__dict__ ---", file=sys.stderr)
    try:
        print(
            json.dumps(
                safe_serialize(readonly_context.__dict__), indent=2, default=str
            ),
            file=sys.stderr,
        )
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)

    # 3. Print session object fully (including private attributes)
    if hasattr(readonly_context, "session"):
        session = readonly_context.session
        print("\n--- session object ---", file=sys.stderr)
        print(f"  type: {type(session).__name__}", file=sys.stderr)
        print(f"  all attrs: {[a for a in dir(session)]}", file=sys.stderr)

        for attr in dir(session):
            try:
                value = getattr(session, attr)
                if not callable(value):
                    print(f"  session.{attr}: {safe_serialize(value)}", file=sys.stderr)
            except Exception as e:
                print(f"  session.{attr}: <error: {e}>", file=sys.stderr)

        # Print session.__dict__ directly
        print("\n--- session.__dict__ ---", file=sys.stderr)
        try:
            print(
                json.dumps(safe_serialize(session.__dict__), indent=2, default=str),
                file=sys.stderr,
            )
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)

        # 4. Print session.state specifically with ALL details
        if hasattr(session, "state"):
            print("\n--- session.state (FULL DUMP) ---", file=sys.stderr)
            try:
                state = session.state
                print(f"  type: {type(state).__name__}", file=sys.stderr)
                print(f"  repr: {repr(state)}", file=sys.stderr)
                print(f"  all attrs: {[a for a in dir(state)]}", file=sys.stderr)

                # Print state.__dict__
                if hasattr(state, "__dict__"):
                    print("\n  state.__dict__:", file=sys.stderr)
                    print(
                        json.dumps(
                            safe_serialize(state.__dict__), indent=4, default=str
                        ),
                        file=sys.stderr,
                    )

                # Try different ways to access state data
                if hasattr(state, "items"):
                    print("\n  state.items():", file=sys.stderr)
                    for k, v in state.items():
                        print(f"    '{k}': {safe_serialize(v)}", file=sys.stderr)
                if hasattr(state, "keys"):
                    print(f"\n  state.keys(): {list(state.keys())}", file=sys.stderr)
                if hasattr(state, "values"):
                    print(
                        f"\n  state.values(): {[safe_serialize(v) for v in state.values()]}",
                        file=sys.stderr,
                    )

                # Try to convert to dict
                try:
                    as_dict = dict(state)
                    print("\n  dict(state):", file=sys.stderr)
                    print(json.dumps(as_dict, indent=4, default=str), file=sys.stderr)
                except Exception as e:
                    print(f"\n  dict(state) failed: {e}", file=sys.stderr)

                # Iterate if iterable
                print("\n  Iterating state keys:", file=sys.stderr)
                try:
                    for i, item in enumerate(state):
                        print(f"    [{i}]: {safe_serialize(item)}", file=sys.stderr)
                        if i > 50:
                            print("    ... (truncated)", file=sys.stderr)
                            break
                except TypeError:
                    print("    (not directly iterable)", file=sys.stderr)
                except Exception as e:
                    print(f"    iteration error: {e}", file=sys.stderr)

            except Exception as e:
                print(f"  Error accessing session.state: {e}", file=sys.stderr)
                import traceback

                traceback.print_exc(file=sys.stderr)

    # 5. Print readonly_context.state if exists
    if hasattr(readonly_context, "state"):
        print("\n--- readonly_context.state ---", file=sys.stderr)
        try:
            state = readonly_context.state
            print(f"  type: {type(state).__name__}", file=sys.stderr)
            print(f"  repr: {repr(state)}", file=sys.stderr)
            if hasattr(state, "__dict__"):
                print(
                    f"  __dict__: {json.dumps(safe_serialize(state.__dict__), indent=4, default=str)}",
                    file=sys.stderr,
                )
            if hasattr(state, "items"):
                print("  items():", file=sys.stderr)
                for k, v in state.items():
                    print(f"    '{k}': {safe_serialize(v)}", file=sys.stderr)
            try:
                as_dict = dict(state)
                print(
                    f"  dict(): {json.dumps(as_dict, indent=4, default=str)}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(f"  dict() failed: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)

    # 6. Check for auth-related attributes anywhere (deeper search)
    print(
        "\n--- Searching for auth/token/credential/key keywords (deep) ---",
        file=sys.stderr,
    )
    found_items = []

    def search_for_auth(obj, path="root", depth=0, visited=None):
        if visited is None:
            visited = set()
        obj_id = id(obj)
        if obj_id in visited or depth > 8:
            return
        visited.add(obj_id)
        try:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key_lower = str(k).lower()
                    if any(
                        kw in key_lower
                        for kw in [
                            "auth",
                            "token",
                            "credential",
                            "oauth",
                            "bearer",
                            "key",
                            "secret",
                            "access",
                        ]
                    ):
                        found_items.append((f"{path}.{k}", safe_serialize(v)))
                    search_for_auth(v, f"{path}.{k}", depth + 1, visited)
            elif hasattr(obj, "__dict__"):
                for k, v in obj.__dict__.items():
                    key_lower = str(k).lower()
                    if any(
                        kw in key_lower
                        for kw in [
                            "auth",
                            "token",
                            "credential",
                            "oauth",
                            "bearer",
                            "key",
                            "secret",
                            "access",
                        ]
                    ):
                        found_items.append((f"{path}.{k}", safe_serialize(v)))
                    search_for_auth(v, f"{path}.{k}", depth + 1, visited)
            elif hasattr(obj, "items"):
                for k, v in obj.items():
                    key_lower = str(k).lower()
                    if any(
                        kw in key_lower
                        for kw in [
                            "auth",
                            "token",
                            "credential",
                            "oauth",
                            "bearer",
                            "key",
                            "secret",
                            "access",
                        ]
                    ):
                        found_items.append((f"{path}.{k}", safe_serialize(v)))
                    search_for_auth(v, f"{path}.{k}", depth + 1, visited)
        except Exception:
            pass

    search_for_auth(readonly_context)
    for path, val in found_items:
        print(f"  FOUND at {path}: {val}", file=sys.stderr)
    if not found_items:
        print("  (no auth-related keys found)", file=sys.stderr)

    print("=" * 80, file=sys.stderr)
    print("END DEBUG DUMP", file=sys.stderr)
    print("=" * 80, file=sys.stderr)


def get_access_token(readonly_context: ReadonlyContext, auth_id: str) -> str | None:
    """Retrieves the OAuth access token from the ReadonlyContext state provided by Agentspace."""

    # Method 1: Try session.state (most common location in Agentspace)
    if hasattr(readonly_context, "session") and hasattr(
        readonly_context.session, "state"
    ):
        try:
            session_state = dict(readonly_context.session.state)

            # Try exact match
            if auth_id in session_state and isinstance(session_state[auth_id], str):
                return session_state[auth_id]

            # Try keys that start with the auth_id (e.g., "auth-0002" matches "auth-0002_123")
            # OR keys that end with the auth_id (e.g., "projects/.../auth-0002")
            for key, value in session_state.items():
                if (
                    (key.startswith(auth_id) or key.endswith(f"/{auth_id}"))
                    and isinstance(value, str)
                    and len(value) > MIN_TOKEN_LENGTH
                ):
                    return value
        except Exception:
            pass

    # Method 2: Try readonly_context.state
    if hasattr(readonly_context, "state"):
        try:
            state_dict = dict(readonly_context.state)
            if auth_id in state_dict and isinstance(state_dict[auth_id], str):
                return state_dict[auth_id]

            # Also check for suffix match in context.state
            for key, value in state_dict.items():
                if (
                    (key.startswith(auth_id) or key.endswith(f"/{auth_id}"))
                    and isinstance(value, str)
                    and len(value) > MIN_TOKEN_LENGTH
                ):
                    return value
        except Exception:
            pass

    # Method 3: Try readonly_context.auth_token
    if hasattr(readonly_context, "auth_token") and readonly_context.auth_token:
        if auth_id in readonly_context.auth_token:
            return readonly_context.auth_token[auth_id]

    # Method 4: Check for managed credentials object (e.g. from OAuth2CredentialExchanger)
    # The exchanger might place a google.oauth2.credentials.Credentials object in the context
    if hasattr(readonly_context, "credentials"):
        creds = readonly_context.credentials
        if hasattr(creds, "token") and creds.token:
            return creds.token

    # Not found - print user-facing error message
    print(f"OAuth token not found for AUTH_ID='{auth_id}'")
    print("User needs to authorize the agent in AgentSpace UI")
    return None
# ABOVE STUFF IS FOR DEBUGGING

def print_tool_context(tool_context: ToolContext):
    """ADK Tool to get email and masked token from Gemini Enterprise"""
    auth_id = os.getenv("AUTH_ID")
    # YOU CAN COMMENT BELOW LINES
    # START
    debug_print_context(tool_context)
    print(get_access_token(tool_context, auth_id))

    state_dict = tool_context.state.to_dict()
    all_keys = state_dict.keys()
    print(all_keys)
    # END
    # get access token using tool context
    access_token = tool_context.state.get(auth_id)
    

    if not access_token:
        return {"error": f"Access token not found in tool_context.state for auth_id: {auth_id} and {all_keys}"}

    
    # mask the token to be returned to the agent
    masked_token = lazy_mask_token(access_token)

    # get the user email using the token
    user_email = get_email_from_token(access_token)
    
    # store email in tool context in case you want to keep referring to it
    tool_context.state["user_email"] = user_email
    return {
        f"temp:{auth_id}": lazy_mask_token(access_token),
        "user_email": user_email,
        "keys":str(all_keys)
    }

# define the root agent
root_agent = Agent(
    name="print_context_agent",
    model="gemini-2.5-flash-lite",
    description=("Agent to print out the items in tool_context.state"),
    instruction="""
        Greet the user first before you respond.
        Return the exact response of `print_tool_context` when asked to print the tool context.
    """,
    tools=[
        print_tool_context,
    ],
)
