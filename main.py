import os
import typing as t
import dotenv
import logging
from github import GithubHandler
from port_ocean.context.ocean import ocean

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


@ocean.on_resync("Repository")
async def resync_repository(kind: str) -> list[dict[str, t.Any]]:
    logger.info(f"Starting repository resync for kind: {kind}")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN is not set")
        raise ValueError("GITHUB_TOKEN is not set")

    handler = GithubHandler(token)
    repositories = await handler.get_repositories()
    logger.info(f"Retrieved {len(repositories)} repositories")

    result = [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "full_name": r["full_name"],
            "private": r["private"],
            "url": r["html_url"],
            "fork": r["fork"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "pushed_at": r["pushed_at"],
            "size": r["size"],
            "stargazers_count": r["stargazers_count"],
        }
        for r in repositories
    ]
    logger.info(f"Processed {len(result)} repositories")
    return result

@ocean.on_resync("PullRequest")
async def resync_pull_requests(kind: str) -> list[dict[str, t.Any]]:
    logger.info(f"Starting pull request resync for kind: {kind}")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN is not set")
        raise ValueError("GITHUB_TOKEN is not set")

    handler = GithubHandler(token)
    repositories = await handler.get_repositories()
    logger.info(f"Retrieved {len(repositories)} repositories for PR sync")
    all_prs = []

    for repo in repositories:
        owner, repo_name = repo["full_name"].split("/")
        logger.info(f"Fetching PRs for repository: {repo_name}")
        prs = await handler.get_pull_requests(owner, repo_name)
        logger.info(f"Retrieved {len(prs)} PRs for {repo_name}")
        all_prs.extend([
            {
                "id": str(pr["id"]),
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "url": pr["html_url"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "repository": repo["full_name"],
                "author": pr["user"]["login"],
                "draft": pr["draft"],
                "merged": pr["merged"],
                "mergeable": pr["mergeable"],
                "mergeable_state": pr["mergeable_state"],
            }
            for pr in prs
        ])

    logger.info(f"Processed total of {len(all_prs)} pull requests")
    return all_prs

@ocean.on_resync("Issue")
async def resync_issues(kind: str) -> list[dict[str, t.Any]]:
    logger.info(f"Starting issue resync for kind: {kind}")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN is not set")
        raise ValueError("GITHUB_TOKEN is not set")

    handler = GithubHandler(token)
    repositories = await handler.get_repositories()
    logger.info(f"Retrieved {len(repositories)} repositories for issue sync")
    all_issues = []

    for repo in repositories:
        owner, repo_name = repo["full_name"].split("/")
        logger.info(f"Fetching issues for repository: {repo_name}")
        issues = await handler.get_issues(owner, repo_name)
        logger.info(f"Retrieved {len(issues)} issues for {repo_name}")
        all_issues.extend([
            {
                "id": str(issue["id"]),
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "url": issue["html_url"],
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "repository": repo["full_name"],
                "author": issue["user"]["login"],
                "labels": [label["name"] for label in issue["labels"]],
                "assignees": [assignee["login"] for assignee in issue["assignees"]],
            }
            for issue in issues
        ])

    logger.info(f"Processed total of {len(all_issues)} issues")
    return all_issues

@ocean.on_resync("Team")
async def resync_teams(kind: str) -> list[dict[str, t.Any]]:
    logger.info(f"Starting team resync for kind: {kind}")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN is not set")
        raise ValueError("GITHUB_TOKEN is not set")

    handler = GithubHandler(token)
    org = os.getenv("GITHUB_ORG")
    if not org:
        logger.debug("GITHUB_ORG is not set. Returning empty list.")
        return []

    logger.info(f"Fetching teams for organization: {org}")
    teams = await handler.get_teams(org)
    logger.info(f"Retrieved {len(teams)} teams")
    
    result = [
        {
            "id": str(team["id"]),
            "name": team["name"],
            "slug": team["slug"],
            "description": team["description"],
            "privacy": team["privacy"],
            "url": team["html_url"],
            "members_count": team["members_count"],
            "repos_count": team["repos_count"],
        }
        for team in teams
    ]
    logger.info(f"Processed {len(result)} teams")
    return result

@ocean.on_resync("Workflow")
async def resync_workflows(kind: str) -> list[dict[str, t.Any]]:
    logger.info(f"Starting workflow resync for kind: {kind}")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN is not set")
        raise ValueError("GITHUB_TOKEN is not set")

    handler = GithubHandler(token)
    repositories = await handler.get_repositories()
    logger.info(f"Retrieved {len(repositories)} repositories for workflow sync")
    all_workflows = []

    for repo in repositories:
        owner, repo_name = repo["full_name"].split("/")
        logger.info(f"Fetching workflows for repository: {repo_name}")
        workflows = await handler.get_workflows(owner, repo_name)
        logger.info(f"Retrieved {len(workflows)} workflows for {repo_name}")
        all_workflows.extend([
            {
                "id": str(workflow["id"]),
                "name": workflow["name"],
                "path": workflow["path"],
                "state": workflow["state"],
                "url": workflow["html_url"],
                "created_at": workflow["created_at"],
                "updated_at": workflow["updated_at"],
                "repository": repo["full_name"],
            }
            for workflow in workflows
        ])

    logger.info(f"Processed total of {len(all_workflows)} workflows")
    return all_workflows

# Optional
# Listen to the start event of the integration. Called once when the integration starts.
@ocean.on_start()
async def on_start() -> None:
    logger.info("Starting ghoceanport integration")
