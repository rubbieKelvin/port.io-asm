import os
import logging
import typing as t
from port_ocean.utils import http_async_client

logger = logging.getLogger(__name__)


class GithubClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.client = http_async_client

    @staticmethod
    def from_env(key: str = "GITHUB_TOKEN") -> "GithubClient":
        token = os.getenv(key)
        if not token:
            logger.error(f'Environment variable "{key}" is not set')
            raise ValueError(f'Environment variable "{key}" is not set')
        return GithubClient(token)

    @property
    def base_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_repositories(self) -> list[dict[str, t.Any]]:
        response = await self.client.get(
            f"{self.base_url}/user/repos", headers=self.base_headers
        )
        return response.json()

    async def get_pull_requests(self, owner: str, repo: str) -> list[dict[str, t.Any]]:
        response = await self.client.get(
            f"{self.base_url}/repos/{owner}/{repo}/pulls",
            headers=self.base_headers,
            params={"state": "all"},
        )
        return response.json()

    async def get_issues(self, owner: str, repo: str) -> list[dict[str, t.Any]]:
        response = await self.client.get(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=self.base_headers,
            params={"state": "all"},
        )
        return response.json()

    async def get_teams(self, org: str) -> list[dict[str, t.Any]]:
        response = await self.client.get(
            f"{self.base_url}/orgs/{org}/teams", headers=self.base_headers
        )
        return response.json()

    async def get_workflows(self, owner: str, repo: str) -> list[dict[str, t.Any]]:
        response = await self.client.get(
            f"{self.base_url}/repos/{owner}/{repo}/actions/workflows",
            headers=self.base_headers,
        )
        return response.json()
