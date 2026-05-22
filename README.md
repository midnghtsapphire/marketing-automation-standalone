# Marketing Automation — Standalone

> Automated affiliate marketing, social media scheduling, TikTok integration, and email campaign builder for Audrey Evans' brand ecosystem.

## Overview

**Marketing Automation Standalone** is a fully self-contained marketing platform that automates the entire workflow from affiliate link generation to social media posting. It uses browser automation (Selenium) instead of APIs to interact with social media platforms, making it work with any platform — including those without public APIs.

### Why This Exists

**The Problem**: Marketing automation tools like HubSpot ($890/month), ActiveCampaign ($49-79/month), and Buffer ($12-120/month) are expensive, API-dependent, and don't support TikTok.

**The Solution**: Self-hosted browser automation that works with ANY platform, costs $7-20/month to run, and includes TikTok support from day one.

**Market Opportunity**: $14.5B marketing automation market (2026) dominated by expensive SaaS tools. Creator economy needs affordable, self-hosted alternatives.

### Blue Ocean Differentiators

1. **Browser Automation** — No API dependency. Works forever, even when APIs change/break.
2. **TikTok Native** — Early mover in TikTok automation space (competitors don't have this).
3. **Self-Hosted** — Complete data ownership, no vendor lock-in, no monthly SaaS fees.
4. **Built on FOSS Dependencies** — Uses open-source components like Python and Flask, while this project remains separately licensed.
5. **98% Cheaper** — $7-20/month vs $49-890/month competitors.

## Features

### Core Modules
- **Affiliate Link Generator** — Automatically creates, tracks, and manages affiliate links for Amazon, Shopify, and custom products with UTM parameters, click tracking, and revenue attribution.
- **Automation Workflow Engine** — End-to-end campaign automation: create campaigns, generate content, schedule posts, and execute across all platforms.
- **Website Integration** — Flask-based web dashboard for managing campaigns, viewing analytics, and controlling the automation pipeline.
- **Browser Automation** — Selenium-powered posting to Instagram, Facebook, Twitter/X, LinkedIn, TikTok, Pinterest, and Lemon8 without API dependencies.
- **Content Templates** — Pre-built, platform-optimized templates for Qahwa Coffee products and DataScope promotions.

### Blue Ocean Enhancements
- **Social Media Scheduler** — Visual content calendar with cross-platform scheduling, optimal posting time suggestions, and queue management.
- **TikTok Integration** — Native TikTok support with trending hashtag discovery, sound integration, and video post scheduling.
- **Email Campaign Builder** — Create, schedule, and track email marketing campaigns with HTML templates, recipient list management, and open/click analytics.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Browser Automation | Selenium + Chrome |
| Database | SQLite |
| Frontend | Jinja2 + Tailwind CSS + Chart.js |
| Image Generation | Pillow |
| Scheduling | APScheduler |
| Deployment | Docker + Gunicorn |

## Quick Start

### Prerequisites
- Python 3.11+
- Google Chrome (for browser automation)

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your credentials

# Run the server
python website_integration.py
# Dashboard at http://localhost:5000
```

### Docker
```bash
# Production
docker-compose up -d

# Development
docker-compose --profile dev up marketing-dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/campaigns` | GET | Campaign management |
| `/create-campaign` | GET/POST | Create new campaign |
| `/launch-campaign/<id>` | POST | Launch a campaign |
| `/social-accounts` | GET | Manage social accounts |
| `/add-social-account` | POST | Add social media account |
| `/affiliate-links` | GET | Affiliate link management |
| `/generate-affiliate-link` | POST | Generate new affiliate link |
| `/content-templates` | GET | Content template library |
| `/analytics` | GET | Campaign analytics dashboard |
| `/api/campaign-status/<id>` | GET | Real-time campaign status |
| `/api/performance-metrics` | GET | Live performance metrics |

## Project Structure

```
marketing-automation-standalone/
├── website_integration.py          # Flask web app (main entry point)
├── automation_workflow.py          # Campaign automation engine
├── affiliate_link_generator.py     # Affiliate link creation & tracking
├── social_media_scheduler.py       # [Blue Ocean] Scheduler + TikTok + Email
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── AUTOMATION_WORKFLOW_GUIDE.md    # Detailed workflow documentation
├── WEBSITE_INTEGRATION_GUIDE.md   # Integration guide
└── README.md
```

## Supported Platforms

| Platform | Post Types | Status |
|----------|-----------|--------|
| Instagram | Image, Carousel, Story | Active |
| Facebook | Text, Image, Video | Active |
| Twitter/X | Tweet, Thread, Media | Active |
| LinkedIn | Post, Article, Image | Active |
| TikTok | Video, Photo Carousel | Blue Ocean |
| Pinterest | Pin, Board | Active |
| Lemon8 | Post | Active |

## Environment Variables

Copy `.env.example` to `.env` and configure. Key variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key |
| `AMAZON_AFFILIATE_TAG` | Amazon Associates tag |
| `TIKTOK_CLIENT_KEY` | TikTok API credentials |
| `SMTP_HOST` | Email server for campaigns |
| `SCHEDULER_TIMEZONE` | Timezone for scheduling |

## License

Proprietary — All rights reserved by Audrey Evans.

---

*Marketing Automation Standalone — Browser-automated marketing for the modern creator.*

---

## Validation

Run the ship readiness check:
```bash
python validate.py
```

All checks should pass:
- ✅ Essential files present
- ✅ HTML templates created
- ✅ Dependencies installed
- ✅ Docker configuration valid
- ✅ Documentation complete
- ✅ Market research documented

## Revvel-Standards / S2M

This repository now carries an explicit local revvel-standards process reference for S2M work requests:

- [`revvel-standards/docs/S2M_PROCESS.md`](revvel-standards/docs/S2M_PROCESS.md) — defines what “S2M” means in this repository and when to create deep-research artifacts.
- [`revvel-standards/docs/XHUMANITY_PROJECT.md`](revvel-standards/docs/XHUMANITY_PROJECT.md) — project charter and project-management setup for the requested `xHumanity` project.

If a work request is marked **S2M**, it should route through these documents before being considered ship-ready.

## Market Position

### Target Customers
1. **Creator Economy** — YouTubers, TikTokers, influencers (10K-500K followers)
2. **Small E-Commerce** — Shopify stores, Amazon sellers, dropshippers
3. **Small Agencies** — 1-5 person marketing agencies managing 5-20 clients

### Competitive Advantages
| Feature | Us | HubSpot | ActiveCampaign | Buffer |
|---------|----|---------|-----------------| -------|
| Monthly Cost | $7-20 | $890 | $49-79 | $12-120 |
| TikTok Support | ✅ | ❌ | ❌ | ❌ |
| API-Free | ✅ | ❌ | ❌ | ❌ |
| Self-Hosted | ✅ | ❌ | ❌ | ❌ |
| Data Ownership | ✅ | ❌ | ❌ | ❌ |

**See [GO_TO_MARKET.md](GO_TO_MARKET.md) for full competitive analysis and launch strategy.**
