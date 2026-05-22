#!/usr/bin/env python3
"""
Quick Start Validation Script
Verifies that Marketing Automation Standalone is ready to ship
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_mark(passed):
    return "✅" if passed else "❌"

def check_files():
    """Check that all essential files exist"""
    print_header("Checking Essential Files")
    
    required_files = [
        'automation_workflow.py',
        'affiliate_link_generator.py',
        'social_media_scheduler.py',
        'website_integration.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        '.env.example',
        '.gitignore',
        'README.md',
        'CHANGELOG.md',
        'DEPLOYMENT_GUIDE.md',
        'GO_TO_MARKET.md',
        'AGENTS.md',
        'revvel-standards/docs/S2M_PROCESS.md',
        'revvel-standards/docs/XHUMANITY_PROJECT.md'
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.isfile(file)
        print(f"{check_mark(exists)} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_templates():
    """Check that HTML templates exist"""
    print_header("Checking HTML Templates")
    
    templates_dir = Path('templates')
    required_templates = [
        'base.html',
        'dashboard.html',
        'campaigns.html',
        'analytics.html'
    ]
    
    all_exist = True
    if not templates_dir.exists():
        print(f"❌ templates/ directory not found")
        return False
    
    for template in required_templates:
        template_path = templates_dir / template
        exists = template_path.is_file()
        print(f"{check_mark(exists)} templates/{template}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check Python dependencies declared in requirements.txt"""
    print_header("Checking Dependencies")
    
    requirements_file = Path('requirements.txt')
    if not requirements_file.is_file():
        print("❌ requirements.txt not found")
        return False
    
    # Mapping of requirement/distribution names to import names (when they differ)
    distribution_to_import = {
        'pillow': 'PIL',  # pip install Pillow, import PIL
        'flask-cors': 'flask_cors',  # pip install flask-cors, import flask_cors
        'python-dotenv': 'dotenv',  # pip install python-dotenv, import dotenv
        'python-dateutil': 'dateutil',  # pip install python-dateutil, import dateutil
        'python-json-logger': 'pythonjsonlogger',  # pip install python-json-logger, import pythonjsonlogger
    }
    
    def parse_requirement_name(line):
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        if line.startswith(('-r', '--', '-e')):
            return None
        
        requirement = line.split('#', 1)[0].strip()
        for separator in ('==', '>=', '<=', '!=', '~=', '>', '<', ';'):
            requirement = requirement.split(separator, 1)[0].strip()
        requirement = requirement.split('[', 1)[0].strip()
        
        return requirement or None
    
    required_distributions = []
    seen = set()
    for line in requirements_file.read_text(encoding='utf-8').splitlines():
        requirement_name = parse_requirement_name(line)
        if requirement_name:
            normalized_name = requirement_name.lower()
            if normalized_name not in seen:
                seen.add(normalized_name)
                required_distributions.append(requirement_name)
    
    all_installed = True
    for distribution in required_distributions:
        normalized_distribution = distribution.lower()
        import_name = distribution_to_import.get(
            normalized_distribution,
            normalized_distribution.replace('-', '_')
        )
        try:
            __import__(import_name)
            note = f" (import as {import_name})" if import_name != distribution else ""
            print(f"✅ {distribution}{note}")
        except ImportError:
            print(f"❌ {distribution} (not installed - run: pip install {distribution})")
            all_installed = False
    
    return all_installed

def check_env_example():
    """Verify .env.example has all required variables"""
    print_header("Checking Environment Configuration")
    
    required_vars = [
        'FLASK_APP',
        'SECRET_KEY',
        'HOST',
        'PORT',
        'SELENIUM_HEADLESS',
        'AMAZON_AFFILIATE_TAG',
        'SMTP_HOST',
        'SCHEDULER_TIMEZONE'
    ]
    
    all_present = True
    
    if not os.path.isfile('.env.example'):
        print("❌ .env.example not found")
        return False
    
    with open('.env.example', 'r') as f:
        env_content = f.read()
    
    for var in required_vars:
        present = f"{var}=" in env_content
        print(f"{check_mark(present)} {var}")
        if not present:
            all_present = False
    
    return all_present

def check_docker():
    """Check Docker configuration"""
    print_header("Checking Docker Configuration")
    
    checks = []
    
    # Check Dockerfile
    if os.path.isfile('Dockerfile'):
        with open('Dockerfile', 'r') as f:
            dockerfile = f.read()
        
        has_chrome = 'google-chrome' in dockerfile.lower()
        has_python = 'python:3.11' in dockerfile.lower()
        has_gunicorn = 'gunicorn' in dockerfile.lower()
        has_healthcheck = 'HEALTHCHECK' in dockerfile
        has_health_endpoint = '/health' in dockerfile
        
        print(f"{check_mark(has_chrome)} Chrome/Selenium installation")
        print(f"{check_mark(has_python)} Python 3.11 base image")
        print(f"{check_mark(has_gunicorn)} Gunicorn WSGI server")
        print(f"{check_mark(has_healthcheck and has_health_endpoint)} Health check configured (/health endpoint)")
        
        checks.extend([has_chrome, has_python, has_gunicorn, has_healthcheck and has_health_endpoint])
    else:
        print("❌ Dockerfile not found")
        return False
    
    # Check docker-compose.yml
    if os.path.isfile('docker-compose.yml'):
        with open('docker-compose.yml', 'r') as f:
            compose = f.read()
        
        has_healthcheck = 'healthcheck:' in compose
        has_health_endpoint = '/health' in compose
        has_ports = '5000:5000' in compose or '${PORT' in compose
        has_volumes = 'volumes:' in compose
        
        print(f"{check_mark(has_healthcheck and has_health_endpoint)} Health check in compose (/health endpoint)")
        print(f"{check_mark(has_ports)} Port mapping configured")
        print(f"{check_mark(has_volumes)} Volume mounting for data")
        
        checks.extend([has_healthcheck and has_health_endpoint, has_ports, has_volumes])
    else:
        print("❌ docker-compose.yml not found")
        return False
    
    return all(checks)

def check_documentation():
    """Check that documentation is complete"""
    print_header("Checking Documentation")
    
    docs = {
        'README.md': ['Quick Start', 'Features', 'Tech Stack', 'Docker'],
        'DEPLOYMENT_GUIDE.md': ['Quick Deploy', 'Production', 'DigitalOcean'],
        'GO_TO_MARKET.md': ['Market Research', 'Competitive Analysis', 'Launch Plan'],
        'CHANGELOG.md': ['[1.0.0]', 'Added', 'Production-Ready'],
        'revvel-standards/docs/S2M_PROCESS.md': ['S2M', 'revvel-standards', 'Deep research'],
        'revvel-standards/docs/XHUMANITY_PROJECT.md': ['xHumanity', 'GitHub Project', 'Linear']
    }
    
    all_complete = True
    
    for doc, keywords in docs.items():
        if os.path.isfile(doc):
            with open(doc, 'r') as f:
                content = f.read()
            
            has_keywords = all(keyword in content for keyword in keywords)
            print(f"{check_mark(has_keywords)} {doc} {'(complete)' if has_keywords else '(missing content)'}")
            if not has_keywords:
                all_complete = False
        else:
            print(f"❌ {doc} (not found)")
            all_complete = False
    
    return all_complete

def check_market_research():
    """Verify market research and positioning is documented"""
    print_header("Checking Market Research & Positioning")
    
    if not os.path.isfile('GO_TO_MARKET.md'):
        print("❌ GO_TO_MARKET.md not found")
        return False
    
    with open('GO_TO_MARKET.md', 'r') as f:
        content = f.read()
    
    checks = {
        'Market size mentioned': '$14.5B' in content or '14.5B' in content,
        'Competitors analyzed': 'HubSpot' in content and 'ActiveCampaign' in content,
        'Blue Ocean positioning': 'Blue Ocean' in content,
        'Browser automation USP': 'browser automation' in content.lower(),
        'TikTok differentiation': 'TikTok' in content,
        'Pricing strategy': '$7' in content or '$890' in content,
        'Target audience defined': 'creator' in content.lower() or 'Creator' in content,
        'Launch plan': 'Launch Plan' in content or 'launch' in content.lower()
    }
    
    for check, passed in checks.items():
        print(f"{check_mark(passed)} {check}")
    
    return all(checks.values())

def main():
    """Run all validation checks"""
    print("\n" + "="*60)
    print("  MARKETING AUTOMATION STANDALONE — SHIP READINESS CHECK")
    print("="*60)
    
    checks = {
        'Essential Files': check_files(),
        'HTML Templates': check_templates(),
        'Dependencies': check_dependencies(),
        'Environment Config': check_env_example(),
        'Docker Setup': check_docker(),
        'Documentation': check_documentation(),
        'Market Research': check_market_research()
    }
    
    # Summary
    print_header("Validation Summary")
    
    for check_name, passed in checks.items():
        print(f"{check_mark(passed)} {check_name}")
    
    # Overall status
    all_passed = all(checks.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("  ✅ READY TO SHIP TO MARKET")
        print("  All checks passed. Deploy with: docker-compose up -d")
    else:
        print("  ❌ NOT READY TO SHIP")
        print("  Some checks failed. Review the issues above.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
