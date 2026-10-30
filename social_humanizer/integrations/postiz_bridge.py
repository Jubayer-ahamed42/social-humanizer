"""
Postiz (Open-Source Social Media Scheduler) API Bridge.
Connects with self-hosted or cloud instances of gitroomhq/postiz-app.
"""

import os
from typing import Dict, Any, Optional, List


class PostizBridge:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initializes Postiz Bridge.
        Uses POSTIZ_API_KEY and POSTIZ_BASE_URL (defaults to https://api.postiz.com).
        """
        self.api_key = api_key or os.getenv("POSTIZ_API_KEY")
        self.base_url = (
            base_url
            or os.getenv("POSTIZ_BASE_URL", "https://api.postiz.com")
        ).rstrip("/")

    def create_post(
        self,
        text: str,
        integration_ids: List[str],
        schedule_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a scheduled or queued post in Postiz.
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Missing POSTIZ_API_KEY. Please set it in environment.",
            }

        import requests

        url = f"{self.base_url}/public/v1/posts"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "content": text,
            "integrations": integration_ids,
        }
        if schedule_time:
            payload["scheduledFor"] = schedule_time

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                return {"success": True, "data": resp.json()}
            return {
                "success": False,
                "error": f"Postiz API error: {resp.status_code} - {resp.text}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
