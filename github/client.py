import os
import logging
import typing as t
from port_ocean.utils import http_async_client
from .types import (
    GithubRepo,
    GithubPullRequest,
    GithubIssue,
    GithubTeam,
    GithubWorkflow,
)

logger = logging.getLogger(__name__)


class GithubError(Exception):
    """Base exception for GitHub API errors."""

    pass


class GithubClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.client = http_async_client
        self.base_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @staticmethod
    def from_env(key: str = "GITHUB_TOKEN") -> "GithubClient":
        token = os.getenv(key)
        if not token:
            logger.error(f'Environment variable "{key}" is not set')
            raise ValueError(f'Environment variable "{key}" is not set')
        return GithubClient(token)

    async def _make_request(self, method: str, url: str, **kwargs: t.Any) -> t.Any:
        """Make a request to the GitHub API with error handling."""
        try:
            response = await self.client.request(
                method, url, headers=self.base_headers, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_msg = f"Failed to make request to {url}: {str(e)}"
            logger.error(error_msg)
            raise GithubError(error_msg) from e

    async def get_repositories(self) -> list[GithubRepo]:
        """Get all repositories for the authenticated user."""
        try:
            logger.info("Fetching repositories")
            data = await self._make_request("GET", f"{self.base_url}/user/repos")
            logger.info(f"Successfully retrieved {len(data)} repositories")
            return t.cast(list[GithubRepo], data)
        except GithubError as e:
            logger.error(f"Failed to fetch repositories: {str(e)}")
            raise

    async def get_pull_requests(self, owner: str, repo: str) -> list[GithubPullRequest]:
        """Get all pull requests for a repository."""
        try:
            logger.info(f"Fetching pull requests for {owner}/{repo}")
            data = await self._make_request(
                "GET",
                f"{self.base_url}/repos/{owner}/{repo}/pulls",
                params={"state": "all"},
            )
            logger.info(
                f"Successfully retrieved {len(data)} pull requests for {owner}/{repo}"
            )
            return t.cast(list[GithubPullRequest], data)
        except GithubError as e:
            logger.error(f"Failed to fetch pull requests for {owner}/{repo}: {str(e)}")
            raise

    async def get_issues(self, owner: str, repo: str) -> list[GithubIssue]:
        """Get all issues for a repository."""
        try:
            logger.info(f"Fetching issues for {owner}/{repo}")
            data = await self._make_request(
                "GET",
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                params={"state": "all"},
            )
            logger.info(f"Successfully retrieved {len(data)} issues for {owner}/{repo}")
            return t.cast(list[GithubIssue], data)
        except GithubError as e:
            logger.error(f"Failed to fetch issues for {owner}/{repo}: {str(e)}")
            raise

    async def get_teams(self, org: str) -> list[GithubTeam]:
        """Get all teams for an organization."""
        try:
            logger.info(f"Fetching teams for organization {org}")
            data = await self._make_request("GET", f"{self.base_url}/orgs/{org}/teams")
            logger.info(f"Successfully retrieved {len(data)} teams for {org}")
            return t.cast(list[GithubTeam], data)
        except GithubError as e:
            logger.error(f"Failed to fetch teams for {org}: {str(e)}")
            raise

    async def get_workflows(self, owner: str, repo: str) -> list[GithubWorkflow]:
        """Get all workflows for a repository."""
        try:
            logger.info(f"Fetching workflows for {owner}/{repo}")
            data = await self._make_request(
                "GET", f"{self.base_url}/repos/{owner}/{repo}/actions/workflows"
            )
            workflows = data.get("workflows", [])
            logger.info(
                f"Successfully retrieved {len(workflows)} workflows for {owner}/{repo}"
            )
            return t.cast(list[GithubWorkflow], workflows)
        except GithubError as e:
            logger.error(f"Failed to fetch workflows for {owner}/{repo}: {str(e)}")
            raise
