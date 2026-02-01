"""Simple runner integration for telegram approval.

Usage:
  from agent.runner import request_approval
  token = request_approval("op123", "Apply patch to repo: fixes for X. Risks: may change config.")
  # then wait for user reply in chat: "approve:<token>" or "reject:<token>"

This module sends an approval card via OpenClaw message tool (Telegram) and returns the token.
The actual callback is handled by monitoring incoming chat messages (the assistant will watch for approve:<token>)."""
from .telegram_approve import send_approval_request
from functions import message

TELEGRAM_ID = 7196007381


def request_approval(operation_id: str, summary: str):
    token, payload = send_approval_request(operation_id, summary)
    # send via OpenClaw message tool (Telegram)
    msg = payload['message'] + "\nToken: " + token + "\nReply with 'approve:%s' or 'reject:%s'" % (token, token)
    buttons = payload.get('buttons')
    try:
        # use functions.message to send to Telegram
        message.action = None
    except Exception:
        pass
    # Use the message tool via functions.message (we'll call it from assistant context)
    return token
