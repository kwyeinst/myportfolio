"""Starter content shown on a fresh install. Edit freely; run `python manage.py seed --reset-content` to reload it."""
import datetime

PROJECTS = [
    dict(title="Test orchestration platform", category="qa", summary="A central system that runs and monitors Playwright suites for 12+ production fintech products, with REST APIs to control runs, queue-based execution, live monitoring and reporting dashboards.", tech="NestJS, Prisma, BullMQ, WebSocket", featured=True, sort_order=1),
    dict(title="AI test failure triage with MCP", category="ai", summary="An intelligent debugging agent leveraging Anthropic's Model Context Protocol (MCP) and Claude to inspect Playwright traces, diagnose flaky failures, and automate root-cause triage for test pipelines.", tech="Anthropic MCP, Claude, Playwright, Python", repo_url="https://github.com/DevMorph77/custom-playwright-mcp", featured=True, sort_order=2),
    dict(title="E-commerce test suite", category="qa", summary="A Playwright framework covering component visibility and functional flows, with Allure reports, scheduled runs and CI/CD automation.", tech="Playwright, Allure", repo_url="https://github.com/DevMorph77/Jumia-Test-Automation.git", featured=True, sort_order=3),
    dict(title="LaundryHub", category="swe", summary="A marketplace connecting customers with laundry providers across Ghana, with JWT authentication, role-based access control and secured API endpoints.", tech="NestJS, Prisma, PostgreSQL", sort_order=4),
    dict(title="Markdown editor", category="swe", summary="A web app for managing Markdown documents with full CRUD, live and full-page previews, and a responsive layout.", tech="React", repo_url="https://github.com/DevMorph77/Browser-Editor", live_url="https://develop--adusei-in-browser-markdown-editor.netlify.app", sort_order=5),
    dict(title="Newspaper app", category="swe", summary="A Django news app with full CRUD, an interactive interface and security measures built in.", tech="Django, Bootstrap", live_url="https://newspaper-project-7.onrender.com", sort_order=6),
]

ACHIEVEMENTS = [
    dict(date=datetime.date(2026, 1, 1), year_only=True, title="Completed Claude Code in Action (Anthropic)"),
    dict(date=datetime.date(2026, 1, 1), year_only=True, title="Completed Introduction to Model Context Protocol (Anthropic)"),
    dict(date=datetime.date(2024, 1, 1), year_only=True, title="Completed the MasterCard Cybersecurity job simulation (Forage)"),
    dict(date=datetime.date(2023, 1, 1), year_only=True, title="Completed the Deloitte Technology job simulation (Forage)"),
    dict(date=datetime.date(2023, 1, 1), year_only=True, title="Completed three Cisco cybersecurity courses"),
]

EXPERIENCES = [
    dict(
        title="QA & Test Automation Engineer",
        organization="fintech and payments company, Ghana",
        period="2024 – Present",
        bullets=(
            "Own test strategy and automation for 12+ live fintech products, including mobile POS, merchant portals, and payment rails.\n"
            "Engineered a centralized queue-based test orchestration platform with NestJS, BullMQ, and WebSockets to run parallel Playwright suites.\n"
            "Discovered critical security vulnerabilities prior to release, including exposed encryption keys and session hijacking vectors.\n"
            "Integrated AI-assisted debugging workflows using Claude and Model Context Protocol (MCP) to trace flaky test failures to root causes.\n"
            "Implemented performance monitoring and reliability tracking with Datadog and Google Analytics."
        ),
        sort_order=1,
    ),
    dict(
        title="Education",
        organization="University of Energy and Natural Resources",
        period="2021 – 2024",
        description="BSc Electrical and Electronics Engineering.",
        sort_order=2,
    ),
]
