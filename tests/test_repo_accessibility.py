"""
Tests to verify GitHub repository accessibility and content.

This module contains automated tests that validate:
- Repository URL is publicly accessible
- Repository can be downloaded as a ZIP file
- Repository contains a README.md file at the root

"""

import requests
import pytest
import zipfile
import io

from urllib.parse import urlparse

GITHUB_REPO: str = "https://github.com/peterintest/automation-evaluation"


def test_github_repo_accessible() -> None:
    """
    Verify that the GitHub repository URL is publicly accessible.
    """
    try:
        response = requests.get(GITHUB_REPO, timeout=10)
        assert response.status_code == 200
    except requests.RequestException:
        assert False, "Failed to access GitHub repository"


def test_can_download_zip() -> None:
    """
    Verify that the repository can be downloaded as a ZIP file.
    """
    try:
        zip_url = f"{GITHUB_REPO}/archive/refs/heads/main.zip"
        response = requests.get(zip_url, timeout=30)

        assert response.status_code == 200, f"Failed to download ZIP: {response.status_code}"

    except (requests.RequestException, zipfile.BadZipFile) as e:
        pytest.fail(f"Failed to download or validate ZIP file: {e}")


def test_contains_readme() -> None:
    """
    Verify that the repository contains a README.md file at the root.
    Supports typical GitHub HTTPS URLs.
    """
    parsed = urlparse(GITHUB_REPO)

    try:
        parts = [p for p in parsed.path.split("/") if p]
        assert len(parts) >= 2, f"Could not extract owner/repo from {GITHUB_REPO}"

        owner, repo = parts[0], parts[1]
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"

        response = requests.get(readme_url, timeout=10)
        assert response.status_code == 200, f"README.md not found (status {response.status_code})"

    except requests.RequestException as e:
        pytest.fail(f"Request to check README.md failed: {e}")
