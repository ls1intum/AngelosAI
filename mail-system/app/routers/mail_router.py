from typing import List

from fastapi import APIRouter, HTTPException, Header, status, Depends
from pydantic import BaseModel

from app.common.environment import config
from app.managers.thread_manager import thread_manager

router = APIRouter()


class MailCredentials(BaseModel):
    mailAccount: str
    mailPassword: str
    studyPrograms: List[str]


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key is None or x_api_key != config.ANGELOS_APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True


@router.post("/{org_id}/start", dependencies=[Depends(verify_api_key)])
def start_thread(org_id: int, creds: MailCredentials):
    """
    Start the mail pipeline for this org with the given credentials.
    If a thread is already running, handle it (stop if ERROR, update credentials if ACTIVE).
    Then we wait for the 'initial connect' event to see if it's truly active or error.
    """
    status_before = thread_manager.get_status(org_id)
    if status_before == "ERROR":
        thread_manager.stop_thread(org_id)

    # Start a new thread if none is running or we stopped it
    status_event = thread_manager.start_thread(org_id, creds.mailAccount, creds.mailPassword, creds.studyPrograms)
    if not status_event:
        status_after = thread_manager.get_status(org_id)
        return {"status": status_after}

    # Wait up to 10 seconds for the connection attempt to finish
    if not status_event.wait(timeout=10):
        # Timeout expired, we do a final check
        final_status = thread_manager.get_status(org_id)
        return {"status": final_status, "info": "Timeout waiting for connect, check status again"}

    final_status = thread_manager.get_status(org_id)
    return {"status": final_status}


@router.post("/{org_id}/stop", dependencies=[Depends(verify_api_key)])
def stop_thread(org_id: int):
    """
    Stop the mail pipeline for this org if it's running.
    """
    success = thread_manager.stop_thread(org_id)
    return {"status": "INACTIVE"}


@router.get("/{org_id}/status", dependencies=[Depends(verify_api_key)])
def get_status(org_id: int):
    """
    Returns the current pipeline status: INACTIVE, ACTIVE, or ERROR
    """
    return {"status": thread_manager.get_status(org_id)}
