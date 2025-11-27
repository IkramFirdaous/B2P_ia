"""
═══════════════════════════════════════════════════════════════════════════════
B2P.AI - COMPREHENSIVE TEST DATABASE GENERATOR
═══════════════════════════════════════════════════════════════════════════════

This script generates a realistic, diversified test database for the B2P.AI
email extraction and task management system.

🎯 FOCUS: Email extraction workflow (ExtractedEmail → ExtractedTask → Task)

📊 DATA GENERATED:
   ✓ 3 Teams with different specializations
   ✓ 12 Employees with varied roles and productivity patterns
   ✓ 18 Skills (Technical, Soft Skills, Domain)
   ✓ 50+ Employee-Skill associations
   ✓ 25 Realistic email scenarios from different senders
   ✓ 50+ Extracted tasks with AI metrics (THE CORE DATASET)
   ✓ 20 Approved tasks converted to actual Task records
   ✓ 360 Burnout metrics (30 days × 12 employees)
   ✓ 12 Achievements across different types
   ✓ 3 Email credentials for Gmail integration

🧠 LOGIC & REALISM:
   - Email scenarios cover: urgent bugs, client requests, meetings, code reviews
   - Urgency levels: Realistic distribution (most are 2-4, few extremes)
   - Confidence scores: 0.65-0.98 (simulates AI uncertainty)
   - Sentiment: Ranges from -0.4 (stressed) to 0.8 (positive)
   - Approval rate: ~60% approved, 40% pending review
   - Burnout patterns: Some employees show increasing stress over time
   - Skills: Each employee has 2-5 skills at different proficiency levels
   - Deadlines: Mix of urgent (1-2 days), normal (3-7 days), long-term (7-14 days)

═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
from datetime import datetime, timedelta, date
from uuid import uuid4, UUID
import random

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.auth import get_password_hash
from app.models import (
    Base, Employee, Team, EmployeeTeam, Skill, EmployeeSkill, SkillCategory, SkillLevel,
    Task, TaskStatus, TaskSource, BurnoutMetric, Achievement, AchievementType,
    ExtractedEmail, ExtractedTask, ExtractionStatus, EmailCredential
)


# ═══════════════════════════════════════════════════════════════════════════════
# REALISTIC EMAIL SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════

REALISTIC_EMAILS = [
    # URGENT PRODUCTION ISSUES
    {
        "subject": "🚨 URGENT: Production Database Connection Failing",
        "sender": "devops@client.com",
        "body": """Hi team,

Our production database is experiencing intermittent connection failures since 2am.
This is affecting ALL users. We need someone to investigate and fix this IMMEDIATELY.

Error logs show: "Connection timeout after 30s"
Server: prod-db-01.aws.internal
Last successful connection: Today 01:47 AM

Please prioritize this above everything else. Client is very unhappy.

Thanks,
DevOps Team""",
        "urgency": 5,
        "sentiment": -0.6,
        "deadline_days": 0.5,  # 12 hours
        "confidence": 0.98,
        "ai_title": "Fix production database connection failures",
        "ai_description": "Investigate and resolve intermittent database connection timeouts on prod-db-01 server affecting all users"
    },

    {
        "subject": "Critical Bug: Payment Processing Failing for EU Customers",
        "sender": "support@company.com",
        "body": """Hello Engineering,

We're receiving multiple reports that EU customers cannot complete payments.
The checkout process hangs at the payment confirmation step.

Affected: ~200 customers in the last 2 hours
Region: EU only (France, Germany, Spain)
Browser: All browsers affected
Error: "Payment gateway timeout"

This needs to be fixed before end of business day. We're losing revenue.

Support Team""",
        "urgency": 5,
        "sentiment": -0.5,
        "deadline_days": 1,
        "confidence": 0.95,
        "ai_title": "Fix payment processing bug for EU customers",
        "ai_description": "Debug and fix payment gateway timeout issue affecting EU customers in checkout flow"
    },

    # CLIENT REQUESTS
    {
        "subject": "Client Request: New Dashboard Features for Q1 Release",
        "sender": "product@company.com",
        "body": """Hi Development Team,

Following our meeting with TechCorp (our biggest client), they've requested
the following features for the Q1 dashboard release:

1. Real-time analytics with auto-refresh every 30 seconds
2. Custom date range filters (currently only preset ranges)
3. Export to Excel functionality
4. Dark mode support

Target delivery: End of next week (Friday, March 15th)
Priority: High - this client represents 30% of our revenue

Let me know if you need clarifications.

Best,
Sarah - Product Manager""",
        "urgency": 4,
        "sentiment": 0.3,
        "deadline_days": 7,
        "confidence": 0.92,
        "ai_title": "Implement dashboard features for TechCorp client",
        "ai_description": "Add real-time analytics, custom date filters, Excel export, and dark mode to Q1 dashboard release"
    },

    {
        "subject": "API Rate Limiting Requirements - ClientX Integration",
        "sender": "partnerships@company.com",
        "body": """Dear API Team,

ClientX is ready to integrate with our API but they need rate limiting
configured for their account:

- Base tier: 1000 requests/hour
- Burst allowance: 1500 requests/hour
- Response header: X-RateLimit-Remaining
- 429 status code when exceeded

Can we have this ready by Wednesday? They want to start testing this week.

Thanks!
Partnership Team""",
        "urgency": 4,
        "sentiment": 0.2,
        "deadline_days": 3,
        "confidence": 0.89,
        "ai_title": "Implement API rate limiting for ClientX",
        "ai_description": "Configure rate limiting (1000 req/hour) with proper headers and 429 responses for ClientX integration"
    },

    # CODE REVIEWS & COLLABORATION
    {
        "subject": "Code Review Request: User Authentication Refactoring",
        "sender": "bob.dupont@b2p.ai",
        "body": """Hey there,

I've finished refactoring the user authentication module to use JWT instead
of session tokens. Can someone review my code?

Branch: feature/jwt-auth-refactor
Files changed: 12 files, +450, -320 lines
Tests: All passing ✓

Main changes:
- Replaced session-based auth with JWT
- Added refresh token rotation
- Improved security with httpOnly cookies
- Updated all auth middleware

Would appreciate feedback by Friday so I can merge before the weekend.

Cheers,
Bob""",
        "urgency": 3,
        "sentiment": 0.5,
        "deadline_days": 4,
        "confidence": 0.88,
        "ai_title": "Review JWT authentication refactoring code",
        "ai_description": "Code review for authentication module refactoring (12 files, JWT implementation) on feature/jwt-auth-refactor branch"
    },

    {
        "subject": "PR Ready: Dark Mode Implementation",
        "sender": "emma.petit@b2p.ai",
        "body": """Hi team,

My dark mode PR is ready for review!

PR #234: https://github.com/company/repo/pull/234
Changes: Added dark mode with theme toggle, respects system preferences
Testing: Manually tested on Chrome, Firefox, Safari

Screenshots attached. Let me know if any changes needed!

Emma""",
        "urgency": 2,
        "sentiment": 0.7,
        "deadline_days": 5,
        "confidence": 0.85,
        "ai_title": "Review dark mode implementation PR #234",
        "ai_description": "Review and provide feedback on dark mode pull request with theme toggle functionality"
    },

    # MEETING FOLLOW-UPS
    {
        "subject": "Action Items from Sprint Planning Meeting",
        "sender": "alice.martin@b2p.ai",
        "body": """Team,

Thanks for the productive sprint planning session today! Here are our action items:

FOR THIS SPRINT (2 weeks):
- Set up CI/CD pipeline for staging environment (David)
- Implement email notification system (Claire)
- Write integration tests for payment API (Bob)
- Update API documentation with new endpoints (François)

DEADLINE: Sprint end (March 22nd)

Please update your tasks in Jira and let me know if any blockers.

Alice""",
        "urgency": 3,
        "sentiment": 0.6,
        "deadline_days": 14,
        "confidence": 0.78,  # Lower confidence - multiple tasks in one email
        "ai_title": "Set up CI/CD pipeline for staging environment",
        "ai_description": "Configure continuous integration and deployment pipeline for staging environment as discussed in sprint planning"
    },

    {
        "subject": "Recap: Architecture Meeting - Microservices Migration",
        "sender": "tech-lead@company.com",
        "body": """Hi Architecture Team,

Key decisions from today's meeting about microservices migration:

PHASE 1 (This Quarter):
1. Split authentication service from monolith
2. Implement API gateway
3. Set up service mesh (Istio)

PHASE 2 (Next Quarter):
1. Extract payment service
2. Extract notification service

Next steps: Each lead should create detailed technical specs for their service
by next Monday.

Questions? Slack me.

Tech Lead""",
        "urgency": 3,
        "sentiment": 0.4,
        "deadline_days": 5,
        "confidence": 0.82,
        "ai_title": "Create technical specs for microservices migration",
        "ai_description": "Draft detailed technical specifications for authentication service extraction and API gateway implementation"
    },

    # BUG REPORTS
    {
        "subject": "Bug Report: Memory Leak in Background Job Processor",
        "sender": "monitoring@company.com",
        "body": """Alert from Production Monitoring:

ISSUE: Memory leak detected in background job processor
SERVICE: worker-03
MEMORY USAGE: Started at 512MB, now at 8.2GB (16 hours runtime)
IMPACT: Worker crashes every 6-8 hours, jobs failing

Logs show memory increasing ~500MB per hour.
Suspect: Job cleanup not releasing resources properly.

Needs investigation ASAP before it affects more workers.

Automated Alert System""",
        "urgency": 5,
        "sentiment": -0.3,
        "deadline_days": 1,
        "confidence": 0.93,
        "ai_title": "Debug memory leak in background job processor",
        "ai_description": "Investigate and fix memory leak in worker-03 causing crashes every 6-8 hours (memory growing 500MB/hour)"
    },

    {
        "subject": "Users Reporting Slow Dashboard Load Times",
        "sender": "support@company.com",
        "body": """Hey Dev Team,

We're getting complaints about the main dashboard taking 10-15 seconds to load.
This started after yesterday's deployment.

Affected users: ~30% of active users
Browser: Mainly Chrome and Edge
Page: /dashboard/overview

Can someone look into what might have changed? Performance was fine last week.

Thanks,
Support""",
        "urgency": 4,
        "sentiment": -0.2,
        "deadline_days": 2,
        "confidence": 0.87,
        "ai_title": "Optimize slow dashboard loading performance",
        "ai_description": "Investigate and fix dashboard performance regression causing 10-15 second load times since yesterday's deployment"
    },

    # DOCUMENTATION & MAINTENANCE
    {
        "subject": "API Documentation Update Needed",
        "sender": "developer-relations@company.com",
        "body": """Hi API Team,

Our API documentation is outdated. External developers are confused about:

1. New authentication endpoints (JWT)
2. Pagination parameters (changed last month)
3. Webhook payload format (updated in v2.1)
4. Rate limiting headers

Can we get the docs updated this week? We have 5 new partners onboarding next Monday.

DevRel Team""",
        "urgency": 3,
        "sentiment": 0.1,
        "deadline_days": 5,
        "confidence": 0.84,
        "ai_title": "Update API documentation for v2.1 changes",
        "ai_description": "Update API docs with JWT auth endpoints, pagination parameters, webhook payloads, and rate limiting information"
    },

    {
        "subject": "Database Migration for User Table - Plan Review",
        "sender": "database-admin@company.com",
        "body": """Team,

Proposed database migration for next maintenance window:

CHANGES:
- Add 'last_login_at' column to users table
- Add 'email_verified_at' column to users table
- Add index on 'created_at' for better query performance
- Migrate 500K existing records

DOWNTIME: ~30 minutes (estimated)
SCHEDULE: Saturday 2:00 AM - 3:00 AM UTC
ROLLBACK PLAN: Automated rollback if issues detected

Need approval from tech lead and QA testing before Saturday.

DBA Team""",
        "urgency": 3,
        "sentiment": 0.3,
        "deadline_days": 3,
        "confidence": 0.91,
        "ai_title": "Review and test database migration plan",
        "ai_description": "Review database migration plan for user table changes and conduct QA testing before Saturday maintenance window"
    },

    # FEATURE REQUESTS (LOWER URGENCY)
    {
        "subject": "Feature Idea: Bulk User Import from CSV",
        "sender": "sales@company.com",
        "body": """Hi Product Team,

Enterprise clients are asking for bulk user import functionality.
They want to upload CSV files with employee data instead of manual entry.

Requirements from clients:
- CSV format support
- Validation before import
- Error reporting for invalid rows
- Support for 1000+ users at once

This would really help with large enterprise deals. Not urgent but would be
great to have in Q2.

Sales Team""",
        "urgency": 2,
        "sentiment": 0.5,
        "deadline_days": 30,
        "confidence": 0.76,
        "ai_title": "Implement bulk user CSV import feature",
        "ai_description": "Develop CSV bulk import functionality with validation, error reporting, and support for 1000+ users"
    },

    {
        "subject": "Enhancement: Add Export to PDF on Reports",
        "sender": "user-feedback@company.com",
        "body": """Hello,

Users are requesting PDF export for their monthly reports.
Currently only Excel export is available.

User quote: "I need to share reports with stakeholders who prefer PDF format"

Feature request: #1456
Votes: 47 users
Priority: Medium

Thanks for considering!

User Feedback Team""",
        "urgency": 2,
        "sentiment": 0.4,
        "deadline_days": 21,
        "confidence": 0.72,
        "ai_title": "Add PDF export functionality to monthly reports",
        "ai_description": "Implement PDF export option for monthly reports alongside existing Excel export (47 user votes)"
    },

    # SECURITY & COMPLIANCE
    {
        "subject": "Security Alert: Dependency Vulnerabilities Detected",
        "sender": "security@company.com",
        "body": """Security Team Alert,

Our automated security scan detected 3 HIGH severity vulnerabilities:

1. lodash@4.17.15 - Prototype Pollution (CVE-2020-8203)
2. axios@0.19.2 - SSRF vulnerability (CVE-2021-3749)
3. jsonwebtoken@8.5.0 - Security bypass (CVE-2022-23529)

ACTION REQUIRED: Update these dependencies and deploy within 48 hours.

All patches are available. Run: npm update

Security Team""",
        "urgency": 5,
        "sentiment": -0.4,
        "deadline_days": 2,
        "confidence": 0.97,
        "ai_title": "Patch security vulnerabilities in dependencies",
        "ai_description": "Update lodash, axios, and jsonwebtoken to patch 3 HIGH severity CVEs detected in security scan"
    },

    {
        "subject": "GDPR Compliance: User Data Export Feature Required",
        "sender": "legal@company.com",
        "body": """Engineering Team,

Per GDPR Article 20, we need to implement user data portability.

REQUIREMENTS:
- Users can request their data export
- Export includes: profile, activity logs, preferences
- Format: JSON or CSV
- Delivery: Email link (expires in 48h)
- Timeline: Must be delivered within 30 days of request

Legal deadline: End of this month.

Legal Team""",
        "urgency": 4,
        "sentiment": 0.0,
        "deadline_days": 10,
        "confidence": 0.94,
        "ai_title": "Implement GDPR user data export feature",
        "ai_description": "Build GDPR-compliant data portability feature allowing users to export profile, logs, and preferences in JSON/CSV"
    },

    # INFRASTRUCTURE & DEVOPS
    {
        "subject": "AWS Cost Optimization Opportunity",
        "sender": "finops@company.com",
        "body": """DevOps Team,

Finance analysis shows we're overspending on AWS:

ISSUES:
- Unused EC2 instances: $2,400/month
- Unattached EBS volumes: $800/month
- Over-provisioned RDS: $1,200/month
- Old snapshots: $400/month

TOTAL WASTE: ~$4,800/month

Can we audit and clean up these resources? Would like to implement
automated cleanup policies too.

FinOps Team""",
        "urgency": 3,
        "sentiment": 0.1,
        "deadline_days": 14,
        "confidence": 0.86,
        "ai_title": "Audit and optimize AWS infrastructure costs",
        "ai_description": "Review and cleanup unused AWS resources (EC2, EBS, RDS, snapshots) to reduce monthly spend by $4,800"
    },

    {
        "subject": "Kubernetes Cluster Upgrade to v1.28",
        "sender": "platform@company.com",
        "body": """Team,

Our Kubernetes cluster is running v1.24 which reaches end-of-life next month.
We need to upgrade to v1.28 (current stable).

PLAN:
1. Test upgrade in dev environment (this week)
2. Upgrade staging (next week)
3. Upgrade production (following weekend)

Compatibility check shows no breaking changes for our workloads.

DevOps""",
        "urgency": 3,
        "sentiment": 0.2,
        "deadline_days": 7,
        "confidence": 0.89,
        "ai_title": "Upgrade Kubernetes cluster to v1.28",
        "ai_description": "Plan and execute Kubernetes cluster upgrade from v1.24 to v1.28 across dev, staging, and production environments"
    },

    # TESTING & QA
    {
        "subject": "QA: Test Coverage Below 60% - Action Needed",
        "sender": "qa-automation@company.com",
        "body": """Dev Team,

Our CI pipeline shows test coverage dropped to 58% (target: 80%).

MODULES WITH LOW COVERAGE:
- Payment processing: 45%
- User authentication: 52%
- Notification service: 38%

This is blocking our production deployment. Can we add tests for critical
paths this week?

QA Team""",
        "urgency": 4,
        "sentiment": -0.1,
        "deadline_days": 5,
        "confidence": 0.83,
        "ai_title": "Increase test coverage for critical modules",
        "ai_description": "Write unit and integration tests to bring payment, auth, and notification modules above 80% coverage"
    },

    {
        "subject": "Load Testing Results - Scaling Issues Found",
        "sender": "performance@company.com",
        "body": """Performance Team Report,

Load testing with 10,000 concurrent users revealed issues:

FINDINGS:
- Database connection pool exhausted at 5,000 users
- API response time >3s under load (target: <500ms)
- Memory usage spike causing OOM errors

RECOMMENDATIONS:
- Increase DB connection pool (currently 50 → suggest 200)
- Implement caching layer (Redis)
- Optimize database queries (found N+1 queries)

We need to fix these before public launch next month.

Performance Team""",
        "urgency": 4,
        "sentiment": -0.2,
        "deadline_days": 12,
        "confidence": 0.91,
        "ai_title": "Fix performance issues found in load testing",
        "ai_description": "Optimize database connections, implement Redis caching, and fix N+1 queries to handle 10K concurrent users"
    },

    # TRAINING & LEARNING
    {
        "subject": "Team Training: New React 18 Features Workshop",
        "sender": "learning@company.com",
        "body": """Hi Frontend Team,

We're organizing a React 18 workshop covering:
- Concurrent rendering
- Automatic batching
- Suspense for data fetching
- New hooks (useTransition, useDeferredValue)

Date: Next Friday 2:00 PM - 5:00 PM
Location: Conference Room B / Zoom link

Please RSVP by Wednesday. Materials will be shared in advance.

L&D Team""",
        "urgency": 2,
        "sentiment": 0.7,
        "deadline_days": 8,
        "confidence": 0.68,
        "ai_title": "Attend React 18 features training workshop",
        "ai_description": "RSVP and attend React 18 workshop on concurrent rendering, Suspense, and new hooks (Friday 2-5 PM)"
    },

    # INCIDENT REPORTS
    {
        "subject": "Post-Mortem: Yesterday's 2-Hour Outage",
        "sender": "incident-response@company.com",
        "body": """Incident Post-Mortem #2024-03-12

INCIDENT: Complete service outage (2 hours 15 minutes)
CAUSE: Database failover triggered by network partition
IMPACT: All users unable to access platform

ACTION ITEMS:
1. Implement better health checks
2. Add automated failover testing
3. Improve monitoring alerts
4. Document runbook procedures

OWNER: Assign tasks to relevant team members
DUE: Next sprint planning

Incident Commander""",
        "urgency": 4,
        "sentiment": -0.3,
        "deadline_days": 7,
        "confidence": 0.88,
        "ai_title": "Implement incident post-mortem action items",
        "ai_description": "Execute post-mortem action items: health checks, failover testing, monitoring improvements, runbook documentation"
    },

    # MISC - INTERNAL PROCESSES
    {
        "subject": "Reminder: Update Your Time Tracking",
        "sender": "hr@company.com",
        "body": """Hello Everyone,

Friendly reminder to log your hours in the time tracking system.

Several people haven't updated for the past 2 weeks. Please update by
end of day Friday for accurate payroll processing.

Thanks!
HR""",
        "urgency": 2,
        "sentiment": 0.3,
        "deadline_days": 4,
        "confidence": 0.65,
        "ai_title": "Update time tracking system",
        "ai_description": "Log hours in time tracking system for the past 2 weeks before Friday deadline"
    },

    {
        "subject": "New Team Member Onboarding - Setup Required",
        "sender": "hr@company.com",
        "body": """IT Team,

New developer starting Monday: Sophie Lambert

SETUP NEEDED:
- Company email account
- GitHub access
- AWS console access
- Slack workspace
- Development machine

Please have everything ready by Monday 9 AM.

Thanks,
HR Team""",
        "urgency": 3,
        "sentiment": 0.5,
        "deadline_days": 3,
        "confidence": 0.79,
        "ai_title": "Setup accounts for new developer Sophie Lambert",
        "ai_description": "Create email, GitHub, AWS, Slack accounts and prepare development machine for new team member starting Monday"
    },

    {
        "subject": "Q1 Performance Reviews Due Next Week",
        "sender": "management@company.com",
        "body": """Team Leads,

Quarterly performance review cycle is here.

DEADLINE: Submit all reviews by next Friday
PROCESS:
1. Self-assessment (employees)
2. Manager review
3. 1-on-1 meeting
4. Final submission

Templates are in the HR portal. Let me know if you need extension.

Management""",
        "urgency": 3,
        "sentiment": 0.2,
        "deadline_days": 9,
        "confidence": 0.73,
        "ai_title": "Complete Q1 performance reviews",
        "ai_description": "Review employee self-assessments, write manager reviews, conduct 1-on-1s, and submit by next Friday"
    },

    {
        "subject": "Server Maintenance Window - Saturday Night",
        "sender": "ops@company.com",
        "body": """All Teams,

Scheduled maintenance this Saturday 11 PM - 3 AM UTC.

PLANNED WORK:
- OS security patches
- Database server upgrades
- Network switch firmware update

EXPECTED IMPACT: Platform unavailable during window

Rollback plan in place. On-call team will monitor.

Ops Team""",
        "urgency": 2,
        "sentiment": 0.1,
        "deadline_days": 4,
        "confidence": 0.70,
        "ai_title": "Prepare for Saturday maintenance window",
        "ai_description": "Review maintenance plan and prepare for 4-hour maintenance window on Saturday 11PM-3AM UTC"
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# DATA GENERATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def clear_database():
    """Drop all tables and recreate them (fresh start)"""
    print("\n" + "="*80)
    print("[DELETE] CLEARING DATABASE...")
    print("="*80)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[OK] Database cleared and recreated\n")


def create_teams(db: Session):
    """Create diverse teams"""
    print("[TEAMS] CREATING TEAMS...")

    teams_data = [
        {
            "name": "Backend Engineering",
            "description": "API development, database architecture, and backend services"
        },
        {
            "name": "Frontend Engineering",
            "description": "React applications, UI/UX implementation, and frontend architecture"
        },
        {
            "name": "DevOps & Infrastructure",
            "description": "Cloud infrastructure, CI/CD, monitoring, and deployment automation"
        },
    ]

    teams = []
    for data in teams_data:
        team = Team(
            id=uuid4(),
            name=data["name"],
            description=data["description"],
            created_at=datetime.now() - timedelta(days=180),  # Team created 6 months ago
        )
        teams.append(team)
        db.add(team)

    db.commit()
    print(f"   [OK] Created {len(teams)} teams")
    return teams


def create_skills(db: Session):
    """Create comprehensive skill set"""
    print("\n[SKILLS] CREATING SKILLS...")

    skills_data = [
        # Technical Skills
        ("Python", SkillCategory.TECHNICAL, "Python programming language and frameworks"),
        ("JavaScript", SkillCategory.TECHNICAL, "JavaScript/TypeScript for web development"),
        ("React", SkillCategory.TECHNICAL, "React.js frontend framework"),
        ("FastAPI", SkillCategory.TECHNICAL, "FastAPI Python web framework"),
        ("PostgreSQL", SkillCategory.TECHNICAL, "PostgreSQL database"),
        ("Docker", SkillCategory.TECHNICAL, "Container orchestration and deployment"),
        ("Kubernetes", SkillCategory.TECHNICAL, "Container orchestration platform"),
        ("AWS", SkillCategory.TECHNICAL, "Amazon Web Services cloud platform"),
        ("Git", SkillCategory.TECHNICAL, "Version control with Git"),
        ("SQL", SkillCategory.TECHNICAL, "SQL database queries and optimization"),

        # Soft Skills
        ("Communication", SkillCategory.SOFT_SKILL, "Effective verbal and written communication"),
        ("Leadership", SkillCategory.SOFT_SKILL, "Team leadership and mentoring"),
        ("Problem Solving", SkillCategory.SOFT_SKILL, "Analytical and creative problem solving"),
        ("Collaboration", SkillCategory.SOFT_SKILL, "Team collaboration and cooperation"),

        # Domain Skills
        ("AI/ML", SkillCategory.DOMAIN, "Artificial Intelligence and Machine Learning"),
        ("System Architecture", SkillCategory.DOMAIN, "Software architecture and system design"),
        ("DevOps", SkillCategory.DOMAIN, "DevOps practices and methodologies"),
        ("Security", SkillCategory.DOMAIN, "Application and infrastructure security"),
    ]

    skills = []
    for name, category, description in skills_data:
        skill = Skill(
            id=uuid4(),
            name=name,
            category=category,
            description=description
        )
        skills.append(skill)
        db.add(skill)

    db.commit()
    print(f"   [OK] Created {len(skills)} skills across {len(set(s[1] for s in skills_data))} categories")
    return skills


def create_employees(db: Session, teams: list, skills: list):
    """Create diverse employees with realistic profiles"""
    print("\n[EMPLOYEES] CREATING EMPLOYEES...")

    # Default password for all test accounts
    default_password_hash = get_password_hash("password123")

    employees_data = [
        {
            "name": "Alice Martin",
            "email": "alice.martin@b2p.ai",
            "role": "Senior Backend Engineer",
            "team_idx": 0,  # Backend team
            "productivity": {"morning": 0.9, "afternoon": 0.85, "evening": 0.5},
            "skills_count": 5
        },
        {
            "name": "Bob Dupont",
            "email": "bob.dupont@b2p.ai",
            "role": "Full Stack Developer",
            "team_idx": 0,
            "productivity": {"morning": 0.7, "afternoon": 0.9, "evening": 0.65},
            "skills_count": 4
        },
        {
            "name": "Claire Bernard",
            "email": "claire.bernard@b2p.ai",
            "role": "Frontend Developer",
            "team_idx": 1,  # Frontend team
            "productivity": {"morning": 0.85, "afternoon": 0.7, "evening": 0.4},
            "skills_count": 4
        },
        {
            "name": "David Leroy",
            "email": "david.leroy@b2p.ai",
            "role": "DevOps Engineer",
            "team_idx": 2,  # DevOps team
            "productivity": {"morning": 0.6, "afternoon": 0.85, "evening": 0.75},
            "skills_count": 5
        },
        {
            "name": "Emma Petit",
            "email": "emma.petit@b2p.ai",
            "role": "UI/UX Frontend Developer",
            "team_idx": 1,
            "productivity": {"morning": 0.95, "afternoon": 0.65, "evening": 0.35},
            "skills_count": 3
        },
        {
            "name": "François Moreau",
            "email": "francois.moreau@b2p.ai",
            "role": "Backend Developer",
            "team_idx": 0,
            "productivity": {"morning": 0.75, "afternoon": 0.8, "evening": 0.6},
            "skills_count": 4
        },
        {
            "name": "Julie Roux",
            "email": "julie.roux@b2p.ai",
            "role": "Junior Frontend Developer",
            "team_idx": 1,
            "productivity": {"morning": 0.8, "afternoon": 0.75, "evening": 0.5},
            "skills_count": 3
        },
        {
            "name": "Thomas Garcia",
            "email": "thomas.garcia@b2p.ai",
            "role": "Site Reliability Engineer",
            "team_idx": 2,
            "productivity": {"morning": 0.7, "afternoon": 0.9, "evening": 0.8},
            "skills_count": 5
        },
        {
            "name": "Sophie Lambert",
            "email": "sophie.lambert@b2p.ai",
            "role": "Senior Frontend Architect",
            "team_idx": 1,
            "productivity": {"morning": 0.9, "afternoon": 0.85, "evening": 0.4},
            "skills_count": 5
        },
        {
            "name": "Lucas Martin",
            "email": "lucas.martin@b2p.ai",
            "role": "Cloud Infrastructure Engineer",
            "team_idx": 2,
            "productivity": {"morning": 0.65, "afternoon": 0.8, "evening": 0.7},
            "skills_count": 4
        },
        {
            "name": "Firdaous Ikram",
            "email": "firdaousikram0402@gmail.com",
            "role": "Full Stack Developer",
            "team_idx": 0,  # Backend team
            "productivity": {"morning": 0.85, "afternoon": 0.9, "evening": 0.6},
            "skills_count": 5
        },
        {
            "name": "Aya Boukhari",
            "email": "ayaboukhari600@gmail.com",
            "role": "Frontend Engineer",
            "team_idx": 1,  # Frontend team
            "productivity": {"morning": 0.8, "afternoon": 0.85, "evening": 0.55},
            "skills_count": 4
        },
    ]

    employees = []
    employee_team_associations = []

    for emp_data in employees_data:
        employee = Employee(
            id=uuid4(),
            name=emp_data["name"],
            email=emp_data["email"],
            password_hash=default_password_hash,
            role=emp_data["role"],
            productivity_periods=emp_data["productivity"],
            created_at=datetime.now() - timedelta(days=random.randint(90, 365))
        )
        employees.append(employee)
        db.add(employee)

    db.flush()  # Flush to get IDs without committing

    # Create team associations
    for i, emp_data in enumerate(employees_data):
        primary_team = teams[emp_data["team_idx"]]

        # Primary team association
        emp_team = EmployeeTeam(
            id=uuid4(),
            employee_id=employees[i].id,
            team_id=primary_team.id,
            is_primary=True,
            joined_at=employees[i].created_at + timedelta(days=1)
        )
        employee_team_associations.append(emp_team)
        db.add(emp_team)

        # Some employees are in multiple teams (cross-functional)
        if random.random() < 0.3:  # 30% chance
            secondary_team = random.choice([t for t in teams if t.id != primary_team.id])
            emp_team2 = EmployeeTeam(
                id=uuid4(),
                employee_id=employees[i].id,
                team_id=secondary_team.id,
                is_primary=False,
                joined_at=employees[i].created_at + timedelta(days=30)
            )
            employee_team_associations.append(emp_team2)
            db.add(emp_team2)

    # Assign manager to teams (convert UUID to string for SQLite)
    teams[0].manager_id = str(employees[0].id)  # Alice manages Backend
    teams[1].manager_id = str(employees[8].id)  # Sophie manages Frontend
    teams[2].manager_id = str(employees[7].id)  # Thomas manages DevOps

    # Assign skills to employees
    employee_skills = []
    for i, emp_data in enumerate(employees_data):
        num_skills = emp_data["skills_count"]
        selected_skills = random.sample(skills, num_skills)

        for skill in selected_skills:
            emp_skill = EmployeeSkill(
                id=uuid4(),
                employee_id=employees[i].id,
                skill_id=skill.id,
                level=random.choice(list(SkillLevel))
            )
            employee_skills.append(emp_skill)
            db.add(emp_skill)

    db.commit()
    print(f"   [OK] Created {len(employees)} employees")
    print(f"   [OK] Created {len(employee_team_associations)} team associations")
    print(f"   [OK] Assigned {len(employee_skills)} employee-skill relationships")
    return employees


def create_email_credentials(db: Session, employees: list):
    """Create Gmail credentials for some employees"""
    print("\n[CREDENTIALS] CREATING EMAIL CREDENTIALS...")

    # Only 3 employees have connected their Gmail (realistic scenario)
    connected_employees = random.sample(employees, 3)

    credentials = []
    for employee in connected_employees:
        cred = EmailCredential(
            id=uuid4(),
            employee_id=str(employee.id),
            email_provider="gmail",
            email_address=employee.email,
            access_token=f"ya29.mock_access_token_{uuid4().hex[:16]}",
            refresh_token=f"1//mock_refresh_token_{uuid4().hex[:24]}",
            token_expiry=datetime.now() + timedelta(hours=1),
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        credentials.append(cred)
        db.add(cred)

    db.commit()
    print(f"   [OK] Created {len(credentials)} Gmail OAuth credentials")
    print(f"   [INFO] Connected: {', '.join([e.name for e in connected_employees])}")
    return credentials, connected_employees


def create_extracted_emails_and_tasks(db: Session, employees_with_gmail: list):
    """
    THE CORE DATASET GENERATOR

    Creates realistic email extraction scenarios with AI-extracted tasks
    """
    print("\n[EMAILS] CREATING EXTRACTED EMAILS & TASKS (THE CORE DATASET)...")

    extracted_emails = []
    extracted_tasks = []

    # Each employee with Gmail gets emails
    for employee in employees_with_gmail:
        # Each employee receives 7-10 emails
        num_emails = random.randint(7, 10)
        selected_email_templates = random.sample(REALISTIC_EMAILS, num_emails)

        for i, email_template in enumerate(selected_email_templates):
            # Create ExtractedEmail record
            email_received_at = datetime.now() - timedelta(
                days=random.randint(0, 14),
                hours=random.randint(0, 23)
            )

            extracted_email = ExtractedEmail(
                id=uuid4(),
                employee_id=str(employee.id),
                email_id=f"gmail_msg_{uuid4().hex[:16]}",  # Mock Gmail message ID
                subject=email_template["subject"],
                sender=email_template["sender"],
                received_at=email_received_at,
                raw_content=email_template["body"],
                extraction_status=ExtractionStatus.COMPLETED,
                extracted_at=email_received_at + timedelta(minutes=random.randint(1, 15)),
                created_at=email_received_at
            )
            extracted_emails.append(extracted_email)
            db.add(extracted_email)
            db.flush()  # Get ID

            # Create ExtractedTask(s) from this email
            # Some emails may have multiple tasks
            num_tasks = random.choices([1, 2, 3], weights=[0.7, 0.25, 0.05])[0]

            for task_idx in range(num_tasks):
                # Calculate deadline
                deadline = None
                if email_template["deadline_days"] is not None:
                    deadline = email_received_at + timedelta(days=email_template["deadline_days"])

                # Determine approval status (60% approved, 40% pending)
                is_approved = random.random() < 0.6
                reviewed_at = None
                if is_approved:
                    reviewed_at = email_received_at + timedelta(
                        hours=random.randint(1, 48)
                    )

                # Add slight randomness to AI scores (simulate real AI behavior)
                confidence_variance = random.uniform(-0.05, 0.05)
                sentiment_variance = random.uniform(-0.1, 0.1)
                urgency_variance = random.choice([-1, 0, 0, 1])  # Usually accurate

                extracted_task = ExtractedTask(
                    id=uuid4(),
                    extracted_email_id=str(extracted_email.id),
                    employee_id=str(employee.id),
                    task_title=email_template["ai_title"] + (f" (Part {task_idx+1})" if num_tasks > 1 else ""),
                    task_description=email_template["ai_description"],
                    deadline=deadline,
                    urgency_level=max(1, min(5, email_template["urgency"] + urgency_variance)),
                    priority_score=max(0.1, min(1.0, email_template["urgency"] / 5.0 + random.uniform(-0.1, 0.1))),
                    sentiment_score=max(-1.0, min(1.0, email_template["sentiment"] + sentiment_variance)),
                    sentiment_label=(
                        "positive" if email_template["sentiment"] > 0.3 else
                        "negative" if email_template["sentiment"] < -0.2 else
                        "neutral"
                    ),
                    confidence_score=max(0.5, min(1.0, email_template["confidence"] + confidence_variance)),
                    approved=is_approved,
                    reviewed_at=reviewed_at,
                    created_task_id=None,  # Will be set when we create actual tasks
                    created_at=extracted_email.extracted_at
                )
                extracted_tasks.append(extracted_task)
                db.add(extracted_task)

    db.commit()

    print(f"   [OK] Created {len(extracted_emails)} extracted emails")
    print(f"   [OK] Created {len(extracted_tasks)} extracted tasks")
    print(f"      [INFO] {sum(1 for t in extracted_tasks if t.approved)} approved (ready to become tasks)")
    print(f"      [INFO] {sum(1 for t in extracted_tasks if not t.approved)} pending review")
    print(f"      [INFO] Urgency distribution: ", end="")
    urgency_dist = {}
    for t in extracted_tasks:
        urgency_dist[t.urgency_level] = urgency_dist.get(t.urgency_level, 0) + 1
    print(", ".join([f"Level {k}: {v}" for k, v in sorted(urgency_dist.items())]))

    return extracted_emails, extracted_tasks


def create_tasks_from_approved_extractions(db: Session, extracted_tasks: list, employees: list):
    """
    Convert approved ExtractedTasks into actual Task records
    This simulates the user clicking "Approve & Create Task" in the UI
    """
    print("\n[TASKS] CONVERTING APPROVED TASKS TO ACTUAL TASKS...")

    approved_extractions = [t for t in extracted_tasks if t.approved]
    tasks = []

    for extracted_task in approved_extractions:
        # Find the employee who received this email
        employee = next((e for e in employees if str(e.id) == extracted_task.employee_id), None)
        if not employee:
            continue

        # Randomly assign to someone (could be the same person or delegated)
        assigned_to = random.choice(employees)

        # Determine status based on deadline
        status = TaskStatus.PENDING
        completed_at = None
        actual_effort = None

        if extracted_task.deadline:
            days_until_deadline = (extracted_task.deadline - datetime.now()).days

            # Some tasks are already completed
            if days_until_deadline < -2:  # Deadline passed
                status = random.choice([TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED])
            elif days_until_deadline < 2:  # Due soon
                status = random.choice([TaskStatus.IN_PROGRESS, TaskStatus.PENDING])

            if status == TaskStatus.COMPLETED:
                completed_at = extracted_task.deadline - timedelta(days=random.randint(0, 2))
                estimated = random.uniform(2.0, 16.0)
                actual_effort = estimated * random.uniform(0.8, 1.3)  # Variance

        # Create Task
        task = Task(
            id=uuid4(),
            title=extracted_task.task_title,
            description=extracted_task.task_description,
            assigned_to=assigned_to.id,
            created_by=employee.id,
            team_id=assigned_to.team_id,  # Assign to the team of assigned person
            urgency=extracted_task.urgency_level,
            difficulty=random.randint(2, 5),  # Difficulty assessed after review
            deadline=extracted_task.deadline,
            estimated_effort=random.uniform(1.0, 16.0),
            status=status,
            priority_score=extracted_task.priority_score,
            dependencies=[],
            source=TaskSource.EMAIL,
            source_metadata={
                "extracted_task_id": str(extracted_task.id),
                "extraction_confidence": extracted_task.confidence_score,
                "email_subject": db.query(ExtractedEmail).filter(
                    ExtractedEmail.id == extracted_task.extracted_email_id
                ).first().subject
            },
            completed_at=completed_at,
            actual_effort=actual_effort,
            created_at=extracted_task.reviewed_at  # Task created when approved
        )
        tasks.append(task)
        db.add(task)
        db.flush()

        # Link back to ExtractedTask
        extracted_task.created_task_id = str(task.id)

    # Add some manual tasks (not from email)
    manual_tasks_data = [
        {
            "title": "Refactor authentication service for better modularity",
            "description": "Break down the monolithic auth service into smaller, testable modules",
            "urgency": 3,
            "difficulty": 4,
            "days_ahead": 10,
            "status": TaskStatus.IN_PROGRESS
        },
        {
            "title": "Write integration tests for payment API",
            "description": "Comprehensive test suite covering all payment endpoints and edge cases",
            "urgency": 3,
            "difficulty": 3,
            "days_ahead": 7,
            "status": TaskStatus.PENDING
        },
        {
            "title": "Update deployment documentation",
            "description": "Document the new Kubernetes deployment process with examples",
            "urgency": 2,
            "difficulty": 2,
            "days_ahead": 14,
            "status": TaskStatus.PENDING
        },
        {
            "title": "Implement Redis caching layer",
            "description": "Add Redis caching for frequently accessed database queries",
            "urgency": 4,
            "difficulty": 4,
            "days_ahead": 5,
            "status": TaskStatus.IN_PROGRESS
        },
        {
            "title": "Code cleanup: Remove deprecated API endpoints",
            "description": "Clean up old v1 API endpoints that are no longer in use",
            "urgency": 2,
            "difficulty": 2,
            "days_ahead": 20,
            "status": TaskStatus.PENDING
        },
    ]

    for task_data in manual_tasks_data:
        assigned_to = random.choice(employees)
        created_by = random.choice([e for e in employees if e.id != assigned_to.id])

        task = Task(
            id=uuid4(),
            title=task_data["title"],
            description=task_data["description"],
            assigned_to=assigned_to.id,
            created_by=created_by.id,
            team_id=assigned_to.team_id,
            urgency=task_data["urgency"],
            difficulty=task_data["difficulty"],
            deadline=datetime.now() + timedelta(days=task_data["days_ahead"]),
            estimated_effort=random.uniform(2.0, 12.0),
            status=task_data["status"],
            priority_score=task_data["urgency"] / 5.0 + random.uniform(-0.1, 0.1),
            source=TaskSource.MANUAL,
            source_metadata={},
            created_at=datetime.now() - timedelta(days=random.randint(1, 10))
        )
        tasks.append(task)
        db.add(task)

    db.commit()

    print(f"   [OK] Created {len(tasks)} actual Task records")
    print(f"      [INFO] {len(approved_extractions)} from approved email extractions")
    print(f"      [INFO] {len(manual_tasks_data)} manual tasks")
    print(f"      [INFO] Status: {sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)} completed, "
          f"{sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)} in progress, "
          f"{sum(1 for t in tasks if t.status == TaskStatus.PENDING)} pending")

    return tasks


def create_burnout_metrics(db: Session, employees: list):
    """
    Generate 30 days of burnout metrics for each employee
    Some employees show increasing stress patterns
    """
    print("\n[BURNOUT] CREATING BURNOUT METRICS (30 DAYS)...")

    metrics = []

    for employee in employees:
        # Determine if this employee is trending toward burnout
        is_stressed = hash(employee.email) % 3 == 0  # 33% of employees

        for days_ago in range(30):
            metric_date = date.today() - timedelta(days=days_ago)

            # Base values
            base_hours = random.uniform(7.0, 9.0)
            base_cognitive_load = random.uniform(0.4, 0.7)
            base_sentiment = random.uniform(0.2, 0.7)

            # Apply stress trend
            if is_stressed:
                stress_progression = (30 - days_ago) / 30.0  # Increases over time
                base_hours += stress_progression * 2.5  # Up to 11.5 hours
                base_cognitive_load += stress_progression * 0.25  # Up to 0.95
                base_sentiment -= stress_progression * 0.5  # Down to -0.3

            # Weekend adjustment (less work)
            if metric_date.weekday() >= 5:  # Saturday or Sunday
                base_hours *= 0.3  # Much less work
                base_cognitive_load *= 0.5

            # Calculate risk score
            overwork_factor = max(0, (base_hours - 8) / 4)  # 0 at 8h, 1 at 12h
            cognitive_factor = base_cognitive_load
            sentiment_factor = max(0, -base_sentiment)  # Negative sentiment increases risk
            risk_score = min(1.0, (overwork_factor + cognitive_factor + sentiment_factor) / 3)

            metric = BurnoutMetric(
                id=uuid4(),
                employee_id=employee.id,
                date=metric_date,
                hours_worked=round(min(base_hours, 14.0), 1),
                breaks_taken=random.randint(1, 4) if metric_date.weekday() < 5 else 0,
                cognitive_load=round(min(base_cognitive_load, 1.0), 2),
                social_interactions=random.randint(2, 12) if metric_date.weekday() < 5 else random.randint(0, 3),
                task_completion_rate=round(random.uniform(0.6, 1.0), 2),
                sentiment_score=round(max(-1.0, min(1.0, base_sentiment)), 2),
                risk_score=round(risk_score, 2),
                created_at=datetime.combine(metric_date, datetime.min.time())
            )
            metrics.append(metric)
            db.add(metric)

    db.commit()

    stressed_employees = [e for e in employees if hash(e.email) % 3 == 0]
    print(f"   [OK] Created {len(metrics)} burnout metrics ({30} days x {len(employees)} employees)")
    print(f"   [WARNING] {len(stressed_employees)} employees showing burnout risk patterns:")
    for emp in stressed_employees:
        latest_risk = next(m.risk_score for m in metrics if m.employee_id == emp.id and m.date == date.today())
        print(f"      [RISK] {emp.name}: Risk score {latest_risk:.2f}")

    return metrics


def create_achievements(db: Session, employees: list, tasks: list):
    """Create diverse achievements for employees"""
    print("\n[ACHIEVEMENTS] CREATING ACHIEVEMENTS...")

    achievements_data = [
        {
            "type": AchievementType.DELIVERABLE,
            "description": "Successfully delivered critical payment system refactor 2 days ahead of schedule",
            "impact_score": 0.95,
            "recognized": True,
            "note": "Outstanding work! The new system is much more reliable."
        },
        {
            "type": AchievementType.INNOVATION,
            "description": "Proposed and implemented automated deployment pipeline reducing deploy time by 70%",
            "impact_score": 0.88,
            "recognized": True,
            "note": "This innovation saved the team countless hours."
        },
        {
            "type": AchievementType.CLIENT_FEEDBACK,
            "description": "Received excellent feedback from ClientX on API integration support",
            "impact_score": 0.82,
            "recognized": False,
            "note": None
        },
        {
            "type": AchievementType.COLLABORATION,
            "description": "Mentored 3 junior developers, all showing significant improvement",
            "impact_score": 0.79,
            "recognized": True,
            "note": "Great mentorship skills!"
        },
        {
            "type": AchievementType.LEARNING,
            "description": "Completed AWS Solutions Architect certification",
            "impact_score": 0.72,
            "recognized": False,
            "note": None
        },
        {
            "type": AchievementType.DELIVERABLE,
            "description": "Fixed critical production bug affecting 10K+ users within 2 hours",
            "impact_score": 0.91,
            "recognized": True,
            "note": "Excellent incident response!"
        },
        {
            "type": AchievementType.INNOVATION,
            "description": "Implemented real-time caching strategy improving API response time by 60%",
            "impact_score": 0.85,
            "recognized": True,
            "note": "Significant performance improvement"
        },
        {
            "type": AchievementType.COLLABORATION,
            "description": "Organized successful knowledge-sharing workshop on React best practices",
            "impact_score": 0.68,
            "recognized": False,
            "note": None
        },
        {
            "type": AchievementType.LEARNING,
            "description": "Completed advanced Kubernetes course and applied learnings to production",
            "impact_score": 0.75,
            "recognized": True,
            "note": "Great initiative for self-improvement"
        },
        {
            "type": AchievementType.CLIENT_FEEDBACK,
            "description": "Client praised the new dashboard interface as 'best-in-class'",
            "impact_score": 0.87,
            "recognized": True,
            "note": "Exceptional UX work!"
        },
        {
            "type": AchievementType.DELIVERABLE,
            "description": "Completed database migration with zero downtime for 1M+ records",
            "impact_score": 0.93,
            "recognized": True,
            "note": "Flawless execution on a complex migration"
        },
        {
            "type": AchievementType.INNOVATION,
            "description": "Created internal tool that automated 15 hours/week of manual QA work",
            "impact_score": 0.84,
            "recognized": False,
            "note": None
        },
    ]

    achievements = []
    completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]

    for ach_data in achievements_data:
        employee = random.choice(employees)
        related_task = random.choice(completed_tasks) if completed_tasks and random.random() < 0.5 else None

        achievement = Achievement(
            id=uuid4(),
            employee_id=employee.id,
            type=ach_data["type"],
            description=ach_data["description"],
            impact_score=ach_data["impact_score"],
            recognized_by_manager=ach_data["recognized"],
            recognition_note=ach_data["note"],
            related_task_id=related_task.id if related_task else None,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60))
        )
        achievements.append(achievement)
        db.add(achievement)

    db.commit()

    print(f"   [OK] Created {len(achievements)} achievements")
    print(f"      [INFO] {sum(1 for a in achievements if a.recognized_by_manager)} recognized by management")
    print(f"      [INFO] Types: ", end="")
    type_dist = {}
    for a in achievements:
        type_dist[a.type.value] = type_dist.get(a.type.value, 0) + 1
    print(", ".join([f"{k}: {v}" for k, v in type_dist.items()]))

    return achievements


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("B2P.AI - COMPREHENSIVE TEST DATABASE GENERATOR")
    print("="*80)
    print("\nThis will generate realistic test data for the B2P.AI email extraction system.")
    print("\n[WARNING] This will DELETE all existing data in the database!")

    # Confirm
    response = input("\nContinue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("\n[CANCELLED] Cancelled by user")
        return

    # Start generation
    start_time = datetime.now()
    db = SessionLocal()

    try:
        # Clear database
        clear_database()

        # Generate data
        teams = create_teams(db)
        skills = create_skills(db)
        employees = create_employees(db, teams, skills)
        credentials, employees_with_gmail = create_email_credentials(db, employees)
        extracted_emails, extracted_tasks = create_extracted_emails_and_tasks(db, employees_with_gmail)
        tasks = create_tasks_from_approved_extractions(db, extracted_tasks, employees)
        metrics = create_burnout_metrics(db, employees)
        achievements = create_achievements(db, employees, tasks)

        # Summary
        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*80)
        print("[SUCCESS] DATABASE GENERATION COMPLETE!")
        print("="*80)

        print(f"\n[SUMMARY]")
        print(f"   Teams:                    {len(teams)}")
        print(f"   Skills:                   {len(skills)}")
        print(f"   Employees:                {len(employees)}")
        print(f"   Gmail Credentials:        {len(credentials)}")
        print(f"   Extracted Emails:         {len(extracted_emails)}")
        print(f"   Extracted Tasks:          {len(extracted_tasks)}")
        print(f"      - Approved:            {sum(1 for t in extracted_tasks if t.approved)}")
        print(f"      - Pending Review:      {sum(1 for t in extracted_tasks if not t.approved)}")
        print(f"   Actual Tasks:             {len(tasks)}")
        print(f"   Burnout Metrics:          {len(metrics)}")
        print(f"   Achievements:             {len(achievements)}")

        print(f"\n[TIMING] Generation time: {duration:.2f} seconds")

        print(f"\n[AUTH] TEST ACCOUNTS (Password: password123):")
        for emp in employees[:6]:
            print(f"   - {emp.email:40s} ({emp.role})")
        print(f"   ... and {len(employees) - 6} more")

        print(f"\n[GMAIL] EMPLOYEES WITH GMAIL CONNECTED:")
        for emp in employees_with_gmail:
            email_count = len([e for e in extracted_emails if str(e.employee_id) == str(emp.id)])
            task_count = len([t for t in extracted_tasks if str(t.employee_id) == str(emp.id)])
            print(f"   - {emp.name:25s} -> {email_count} emails, {task_count} extracted tasks")

        print(f"\n[NEXT STEPS]")
        print(f"   1. Start backend:  cd backend && uvicorn app.main:app --reload")
        print(f"   2. Start frontend: cd frontend && npm start")
        print(f"   3. Login with any test account above")
        print(f"   4. Navigate to Email Extraction page to see extracted tasks")
        print(f"   5. Test approving/rejecting extracted tasks")

        print(f"\n[TESTING] EMAIL EXTRACTION FEATURE:")
        print(f"   - Go to /email-extraction page")
        print(f"   - View {sum(1 for t in extracted_tasks if not t.approved)} pending tasks")
        print(f"   - Click 'View Details' to see AI extraction metadata")
        print(f"   - Approve tasks to convert them to actual Task records")
        print(f"   - Check different urgency levels and confidence scores")

        print("\n" + "="*80)

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
