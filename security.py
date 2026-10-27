"""Protect the scheduled-job endpoints.

The service runs on Cloud Run with public access, and every endpoint here
either posts to Instagram/Threads or spends AI credits. Callers (Cloud Scheduler)
must send `X-Job-Token: <JOB_TOKEN>`. If JOB_TOKEN is not set, every request is rejected.
"""
import functools
import hmac
import os

from flask import request  # type: ignore


def verify_job_token(token: str | None) -> bool:
    expected = os.environ.get("JOB_TOKEN", "")
    if not expected or not token:
        return False
    return hmac.compare_digest(expected.encode("utf-8"), token.encode("utf-8"))


def require_job_token(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not verify_job_token(request.headers.get("X-Job-Token")):
            if not os.environ.get("JOB_TOKEN"):
                print("JOB_TOKEN is not set; rejecting request")
            return "Forbidden", 403
        return view(*args, **kwargs)

    return wrapper
