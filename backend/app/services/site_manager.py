import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger


SITES_DB_PATH = "./data/sites.json"


class SiteManager:
    def __init__(self):
        os.makedirs("./data", exist_ok=True)
        self._sites: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(SITES_DB_PATH):
            try:
                with open(SITES_DB_PATH, "r") as f:
                    self._sites = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load sites DB: {e}")
                self._sites = {}

    def _save(self):
        try:
            with open(SITES_DB_PATH, "w") as f:
                json.dump(self._sites, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save sites DB: {e}")

    def generate_site_id(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def create_site(self, url: str) -> str:
        site_id = self.generate_site_id(url)
        self._sites[site_id] = {
            "site_id": site_id,
            "url": url,
            "title": url,
            "pages_count": 0,
            "chunks_count": 0,
            "status": "crawling",
            "ingested_at": datetime.utcnow().isoformat(),
            "suggested_questions": [],
        }
        self._save()
        return site_id

    def update_site(self, site_id: str, **kwargs):
        if site_id in self._sites:
            self._sites[site_id].update(kwargs)
            self._save()

    def get_site(self, site_id: str) -> Optional[dict]:
        return self._sites.get(site_id)

    def get_all_sites(self) -> List[dict]:
        return list(self._sites.values())

    def delete_site(self, site_id: str) -> bool:
        if site_id in self._sites:
            del self._sites[site_id]
            self._save()
            return True
        return False

    def site_exists(self, site_id: str) -> bool:
        return site_id in self._sites


site_manager = SiteManager()
