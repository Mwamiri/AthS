# Security Automation (No VS Code Needed)

This repo is now configured so you can monitor and patch backend security directly from GitHub web/mobile.

## What is automated

- **Dependabot PRs** for Python dependencies in `src/backend/requirements.txt`
- **Dependabot PRs** for GitHub Actions updates
- **Daily security workflow** (`Security Monitor`) that runs:
  - `pip-audit`
  - `safety`
  - `bandit`

Files:

- `.github/dependabot.yml`
- `.github/workflows/security-monitor.yml`
- `.github/workflows/dependabot-auto-merge.yml`

## How you will know about upgrades and vulnerabilities

### 1) GitHub Dependabot Alerts

- Open your repository on GitHub
- Go to **Security** tab
- Review **Dependabot alerts** and **Dependency graph**

### 2) Pull Request notifications

- Dependabot creates PRs automatically
- You get notifications by email/mobile (if enabled)

### 3) Actions failures

- `Security Monitor` fails if dependency vulnerabilities are found by `pip-audit`
- You get GitHub Actions failure notifications

## How to patch from GitHub only

1. Open Dependabot PR
2. Review CI checks and security report artifacts
3. Click **Merge** (or **Squash and merge**) in GitHub UI
4. Deployment pipeline runs normally after merge

No local IDE is required for standard security patching.

## Auto-merge behavior

- Dependabot Python patch PRs are configured for auto-merge.
- Merge only happens after required status checks pass.
- Major/minor updates still require manual review and merge.

## Recommended GitHub settings (one-time)

In repository settings:

- Enable **Dependabot alerts**
- Enable **Dependabot security updates**
- Enable **Secret scanning** and **Push protection**
- Require status checks before merge (CI + Security Monitor)

## Optional hardening

- Add CODEOWNERS for mandatory security review
- Auto-merge Dependabot patch updates only after green checks
- Add Slack/Teams webhook notification for failed security workflow
