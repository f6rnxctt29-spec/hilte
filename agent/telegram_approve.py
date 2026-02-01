"""Telegram one-click approval stub.

Sends approval cards to the operator (configured TELEGRAM_ID) via OpenClaw message tool.
When a blocked operation occurs, call send_approval_request(operation_id, summary) and
wait for callback (Approve/Reject). The callback handling is performed by the agent runner
and maps the approval to the pending operation.

This is a minimal, local-only implementation: it composes the message payload for the
OpenClaw `message` tool. The actual receiving of callbacks depends on the messaging
integration (Telegram). For now, the send_approval_request returns a token that the
runner will poll via message tool (or you can implement webhook callbacks).
"""
from datetime import datetime
import uuid

TELEGRAM_OPERATOR_ID = 7196007381


def send_approval_request(operation_id: str, summary: str):
    """Compose approval payload. Caller should use message tool to send it.
    Returns approval token (for local tracking).
    """
    token = str(uuid.uuid4())
    payload = {
        "to": str(TELEGRAM_OPERATOR_ID),
        "message": f"Approval request: {operation_id}\n{summary}\nApprove?",
        "buttons": [[{"text": "Approve", "callback_data": f"approve:{token}"}, {"text": "Reject", "callback_data": f"reject:{token}"}]]
    }
    # The caller will call message action=send with this payload.
    return token, payload
