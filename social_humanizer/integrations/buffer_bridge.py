"""
Buffer API Connector for scheduling humanized posts.
Official Buffer API v1 wrapper.
"""

import os
from typing import Dict, Any, Optional, List


class BufferBridge:
    def __init__(self, access_token: Optional[str] = None):
        """
        Initializes Buffer Bridge.
        Uses BUFFER_ACCESS_TOKEN from environment if not supplied.
        """
        self.access_token = access_token or os.getenv("BUFFER_ACCESS_TOKEN")
        self.base_url = "https://api.bufferapp.com/1"

    def schedule_post(
        self,
        text: str,
        profile_ids: List[str],
        now: bool = False,
    ) -> Dict[str, Any]:
        """
        Adds an update to Buffer queue.
        - text: The humanized post content.
        - profile_ids: List of connected social media profile IDs.
        - now: If True, post immediately. If False, add to queue.
        """
        if not self.access_token:
            return {
                "success": False,
                "error": "Missing BUFFER_ACCESS_TOKEN. Please set it in environment.",
            }

        import requests

        url = f"{self.base_url}/updates/create.json"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {
            "text": text,
            "profile_ids[]": profile_ids,
            "now": now,
        }

        try:
            resp = requests.post(url, data=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                return {"success": True, "data": resp.json()}
            return {
                "success": False,
                "error": f"Buffer API error: {resp.status_code} - {resp.text}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
