#!/usr/bin/env python3
"""
Website Integration System for Marketing Automation
Marketing Automation Standalone - Web Interface
"""

import json
import datetime
import sqlite3
import hashlib
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import logging
from automation_workflow import AutomationWorkflow, Campaign
from affiliate_link_generator import AffiliateLinkGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)

# Initialize automation systems
automation_workflow = AutomationWorkflow()
affiliate_generator = AffiliateLinkGenerator()

@dataclass
class WebsiteIntegration:
    """Main integration class for website functionality"""
    
    def __init__(self):
        self.workflow = AutomationWorkflow()
        self.affiliate_gen = AffiliateLinkGenerator()
        self.init_web_database()
    
    def init_web_database(self):
        """Initialize additional database tables for web interface"""
        conn = sqlite3.connect('marketing_automation.db')
        cursor = conn.cursor()
        
        # User campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT UNIQUE,
                name TEXT,
                status TEXT DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                scheduled_start DATETIME,
                products TEXT,  -- JSON array
                platforms TEXT, -- JSON array
                budget REAL,
                results TEXT    -- JSON object
            )
        ''')
        
        # Social media accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                username TEXT,
                encrypted_password TEXT,
                status TEXT DEFAULT 'inactive',
                last_login DATETIME,
                posts_today INTEGER DEFAULT 0,
                daily_limit INTEGER DEFAULT 10
            )
        ''')
        
        # Content templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                platform TEXT,
                template_type TEXT, -- caption, hashtags, cta
                content TEXT,
                performance_score REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Campaign analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                date DATE,
                platform TEXT,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                cost REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()

# Initialize integration
web_integration = WebsiteIntegration()

# Web Routes

@app.route('/')
def dashboard():
    """Main dashboard showing campaign overview"""
    
    # Get recent campaigns
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT campaign_id, name, status, created_at, budget, results
        FROM user_campaigns 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    
    campaigns = []
    for row in cursor.fetchall():
        campaign_data = {
            'campaign_id': row[0],
            'name': row[1],
            'status': row[2],
            'created_at': row[3],
            'budget': row[4],
            'results': json.loads(row[5]) if row[5] else {}
        }
        campaigns.append(campaign_data)
    
    # Get overall performance metrics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_campaigns,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_campaigns,
            AVG(budget) as avg_budget
        FROM user_campaigns
    ''')
    
    stats = cursor.fetchone()
    
    # Get affiliate performance
    affiliate_report = affiliate_generator.generate_link_report()
    
    conn.close()
    
    dashboard_data = {
        'campaigns': campaigns,
        'stats': {
            'total_campaigns': stats[0] or 0,
            'active_campaigns': stats[1] or 0,
            'avg_budget': stats[2] or 0,
            'total_revenue': affiliate_report['overall_performance']['total_revenue'],
            'total_clicks': affiliate_report['overall_performance']['total_clicks'],
            'conversion_rate': affiliate_report['overall_performance']['overall_conversion_rate']
        },
        'affiliate_performance': affiliate_report
    }
    
    return render_template('dashboard.html', data=dashboard_data)

@app.route('/campaigns')
def campaigns():
    """Campaign management page"""
    
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT campaign_id, name, status, created_at, scheduled_start, 
               products, platforms, budget, results
        FROM user_campaigns 
        ORDER BY created_at DESC
    ''')
    
    campaigns = []
    for row in cursor.fetchall():
        campaign_data = {
            'campaign_id': row[0],
            'name': row[1],
            'status': row[2],
            'created_at': row[3],
            'scheduled_start': row[4],
            'products': json.loads(row[5]) if row[5] else [],
            'platforms': json.loads(row[6]) if row[6] else [],
            'budget': row[7],
            'results': json.loads(row[8]) if row[8] else {}
        }
        campaigns.append(campaign_data)
    
    conn.close()
    
    return render_template('campaigns.html', campaigns=campaigns)

@app.route('/create-campaign', methods=['GET', 'POST'])
def create_campaign():
    """Create new marketing campaign"""
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Create campaign using automation workflow
        campaign = automation_workflow.create_campaign(
            name=data['name'],
            products=data['products'],
            platforms=data['platforms'],
            duration_days=data.get('duration_days', 7),
            budget=data.get('budget', 500.0)
        )
        
        # Store in database
        conn = sqlite3.connect('marketing_automation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_campaigns 
            (campaign_id, name, status, scheduled_start, products, platforms, budget)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign.campaign_id,
            campaign.name,
            'draft',
            campaign.start_date.isoformat(),
            json.dumps(campaign.products),
            json.dumps(campaign.platforms),
            campaign.budget
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'campaign_id': campaign.campaign_id,
            'message': 'Campaign created successfully!'
        })
    
    # GET request - show campaign creation form
    available_products = list(automation_workflow.affiliate_generator.products.keys())
    available_platforms = list(automation_workflow.social_accounts.keys())
    
    return render_template('create_campaign.html', 
                         products=available_products, 
                         platforms=available_platforms)

@app.route('/launch-campaign/<campaign_id>', methods=['POST'])
def launch_campaign(campaign_id):
    """Launch a campaign for execution"""
    
    # Get campaign from database
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, products, platforms, budget
        FROM user_campaigns 
        WHERE campaign_id = ?
    ''', (campaign_id,))
    
    campaign_data = cursor.fetchone()
    if not campaign_data:
        return jsonify({'success': False, 'message': 'Campaign not found'})
    
    # Get social media credentials (in production, these would be encrypted)
    cursor.execute('''
        SELECT platform, username, encrypted_password
        FROM social_accounts
        WHERE status = 'active'
    ''')
    
    credentials = {}
    for row in cursor.fetchall():
        credentials[row[0]] = {
            'username': row[1],
            'password': row[2]  # In production, decrypt this
        }
    
    conn.close()
    
    # Create campaign object
    campaign = automation_workflow.create_campaign(
        name=campaign_data[0],
        products=json.loads(campaign_data[1]),
        platforms=json.loads(campaign_data[2]),
        budget=campaign_data[3]
    )
    campaign.campaign_id = campaign_id  # Use existing ID
    
    # Execute campaign
    try:
        results = automation_workflow.execute_campaign(campaign, credentials)
        
        # Update database with results
        conn = sqlite3.connect('marketing_automation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_campaigns 
            SET status = 'completed', results = ?
            WHERE campaign_id = ?
        ''', (json.dumps(results), campaign_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Campaign launched! Success rate: {results["success_rate"]:.1f}%'
        })
        
    except Exception as e:
        logger.error(f"Campaign launch failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Campaign launch failed: {str(e)}'
        })

@app.route('/social-accounts')
def social_accounts():
    """Manage social media accounts"""
    
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT platform, username, status, last_login, posts_today, daily_limit
        FROM social_accounts
        ORDER BY platform
    ''')
    
    accounts = []
    for row in cursor.fetchall():
        accounts.append({
            'platform': row[0],
            'username': row[1],
            'status': row[2],
            'last_login': row[3],
            'posts_today': row[4],
            'daily_limit': row[5]
        })
    
    conn.close()
    
    return render_template('social_accounts.html', accounts=accounts)

@app.route('/add-social-account', methods=['POST'])
def add_social_account():
    """Add new social media account"""
    
    data = request.get_json()
    
    # In production, encrypt the password
    encrypted_password = data['password']  # Placeholder - implement encryption
    
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO social_accounts 
        (platform, username, encrypted_password, status, daily_limit)
        VALUES (?, ?, ?, 'active', ?)
    ''', (
        data['platform'],
        data['username'],
        encrypted_password,
        data.get('daily_limit', 10)
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'{data["platform"]} account added successfully!'
    })

@app.route('/affiliate-links')
def affiliate_links():
    """Manage affiliate links and performance"""
    
    # Get affiliate link performance report
    report = affiliate_generator.generate_link_report()
    
    # Get recent links
    conn = sqlite3.connect('affiliate_links.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT link_id, product_name, campaign, medium, source, 
               created_at, clicks, conversions, revenue
        FROM affiliate_links 
        ORDER BY created_at DESC 
        LIMIT 50
    ''')
    
    recent_links = []
    for row in cursor.fetchall():
        recent_links.append({
            'link_id': row[0],
            'product_name': row[1],
            'campaign': row[2],
            'medium': row[3],
            'source': row[4],
            'created_at': row[5],
            'clicks': row[6],
            'conversions': row[7],
            'revenue': row[8],
            'conversion_rate': (row[7] / row[6] * 100) if row[6] > 0 else 0
        })
    
    conn.close()
    
    return render_template('affiliate_links.html', 
                         report=report, 
                         recent_links=recent_links)

@app.route('/generate-affiliate-link', methods=['POST'])
def generate_affiliate_link():
    """Generate new affiliate link"""
    
    data = request.get_json()
    
    try:
        link = affiliate_generator.create_affiliate_link(
            product_id=data['product_id'],
            campaign=data.get('campaign', 'manual'),
            medium=data.get('medium', 'social'),
            source=data.get('source', 'website')
        )
        
        short_link = affiliate_generator.create_short_link(link)
        
        return jsonify({
            'success': True,
            'affiliate_link': link.affiliate_url,
            'short_link': short_link,
            'tracking_code': link.tracking_code
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/content-templates')
def content_templates():
    """Manage content templates"""
    
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_id, platform, template_type, content, performance_score
        FROM content_templates
        ORDER BY performance_score DESC
    ''')
    
    templates = []
    for row in cursor.fetchall():
        templates.append({
            'product_id': row[0],
            'platform': row[1],
            'template_type': row[2],
            'content': row[3],
            'performance_score': row[4]
        })
    
    conn.close()
    
    return render_template('content_templates.html', templates=templates)

@app.route('/analytics')
def analytics():
    """Campaign analytics and performance dashboard"""
    
    # Get campaign analytics
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    # Daily performance over last 30 days
    cursor.execute('''
        SELECT date, SUM(impressions), SUM(clicks), SUM(conversions), SUM(revenue)
        FROM campaign_analytics
        WHERE date >= date('now', '-30 days')
        GROUP BY date
        ORDER BY date
    ''')
    
    daily_performance = []
    for row in cursor.fetchall():
        daily_performance.append({
            'date': row[0],
            'impressions': row[1] or 0,
            'clicks': row[2] or 0,
            'conversions': row[3] or 0,
            'revenue': row[4] or 0.0
        })
    
    # Platform performance
    cursor.execute('''
        SELECT platform, SUM(clicks), SUM(conversions), SUM(revenue)
        FROM campaign_analytics
        WHERE date >= date('now', '-30 days')
        GROUP BY platform
        ORDER BY revenue DESC
    ''')
    
    platform_performance = []
    for row in cursor.fetchall():
        platform_performance.append({
            'platform': row[0],
            'clicks': row[1] or 0,
            'conversions': row[2] or 0,
            'revenue': row[3] or 0.0,
            'conversion_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
        })
    
    conn.close()
    
    # Get affiliate link analytics
    affiliate_report = affiliate_generator.generate_link_report()
    
    analytics_data = {
        'daily_performance': daily_performance,
        'platform_performance': platform_performance,
        'affiliate_report': affiliate_report,
        'summary': {
            'total_revenue': sum(day['revenue'] for day in daily_performance),
            'total_clicks': sum(day['clicks'] for day in daily_performance),
            'total_conversions': sum(day['conversions'] for day in daily_performance),
            'avg_conversion_rate': affiliate_report['overall_performance']['overall_conversion_rate']
        }
    }
    
    return render_template('analytics.html', data=analytics_data)

@app.route('/api/campaign-status/<campaign_id>')
def campaign_status(campaign_id):
    """Get real-time campaign status"""
    
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT status, results FROM user_campaigns WHERE campaign_id = ?
    ''', (campaign_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'status': result[0],
            'results': json.loads(result[1]) if result[1] else {}
        })
    else:
        return jsonify({'error': 'Campaign not found'}), 404

@app.route('/api/performance-metrics')
def performance_metrics():
    """Get real-time performance metrics for dashboard"""
    
    # Get today's performance
    conn = sqlite3.connect('marketing_automation.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(clicks), SUM(conversions), SUM(revenue)
        FROM campaign_analytics
        WHERE date = date('now')
    ''')
    
    today_stats = cursor.fetchone()
    
    # Get affiliate performance
    affiliate_report = affiliate_generator.generate_link_report()
    
    conn.close()
    
    return jsonify({
        'today': {
            'clicks': today_stats[0] or 0,
            'conversions': today_stats[1] or 0,
            'revenue': today_stats[2] or 0.0
        },
        'overall': affiliate_report['overall_performance']
    })

# HTML Templates (these would be in templates/ directory)

def create_html_templates():
    """Create HTML templates for the web interface"""
    
    os.makedirs('templates', exist_ok=True)
    
    # Dashboard template
    dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Automation Dashboard - Meet Audrey Evans</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-100">
    <nav class="bg-purple-600 text-white p-4">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">Marketing Automation</h1>
            <div class="space-x-4">
                <a href="/" class="hover:underline">Dashboard</a>
                <a href="/campaigns" class="hover:underline">Campaigns</a>
                <a href="/affiliate-links" class="hover:underline">Affiliate Links</a>
                <a href="/analytics" class="hover:underline">Analytics</a>
                <a href="/social-accounts" class="hover:underline">Social Accounts</a>
            </div>
        </div>
    </nav>

    <div class="container mx-auto p-6">
        <h2 class="text-3xl font-bold mb-6">Dashboard</h2>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-600">Total Campaigns</h3>
                <p class="text-3xl font-bold text-purple-600">{{ data.stats.total_campaigns }}</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-600">Active Campaigns</h3>
                <p class="text-3xl font-bold text-green-600">{{ data.stats.active_campaigns }}</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-600">Total Revenue</h3>
                <p class="text-3xl font-bold text-blue-600">${{ "%.2f"|format(data.stats.total_revenue) }}</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-semibold text-gray-600">Conversion Rate</h3>
                <p class="text-3xl font-bold text-orange-600">{{ "%.1f"|format(data.stats.conversion_rate) }}%</p>
            </div>
        </div>

        <!-- Recent Campaigns -->
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h3 class="text-xl font-bold mb-4">Recent Campaigns</h3>
            <div class="overflow-x-auto">
                <table class="w-full table-auto">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-4 py-2 text-left">Campaign Name</th>
                            <th class="px-4 py-2 text-left">Status</th>
                            <th class="px-4 py-2 text-left">Budget</th>
                            <th class="px-4 py-2 text-left">Created</th>
                            <th class="px-4 py-2 text-left">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for campaign in data.campaigns %}
                        <tr class="border-b">
                            <td class="px-4 py-2">{{ campaign.name }}</td>
                            <td class="px-4 py-2">
                                <span class="px-2 py-1 rounded text-sm 
                                    {% if campaign.status == 'active' %}bg-green-100 text-green-800
                                    {% elif campaign.status == 'completed' %}bg-blue-100 text-blue-800
                                    {% else %}bg-gray-100 text-gray-800{% endif %}">
                                    {{ campaign.status.title() }}
                                </span>
                            </td>
                            <td class="px-4 py-2">${{ "%.2f"|format(campaign.budget) }}</td>
                            <td class="px-4 py-2">{{ campaign.created_at[:10] }}</td>
                            <td class="px-4 py-2">
                                <button onclick="viewCampaign('{{ campaign.campaign_id }}')" 
                                        class="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700">
                                    View
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-bold mb-4">Quick Actions</h3>
                <div class="space-y-3">
                    <a href="/create-campaign" class="block bg-purple-600 text-white text-center py-2 rounded hover:bg-purple-700">
                        Create New Campaign
                    </a>
                    <button onclick="generateQuickLink()" class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">
                        Generate Affiliate Link
                    </button>
                    <a href="/analytics" class="block bg-blue-600 text-white text-center py-2 rounded hover:bg-blue-700">
                        View Analytics
                    </a>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-bold mb-4">Platform Performance</h3>
                <canvas id="platformChart" width="400" height="200"></canvas>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="text-lg font-bold mb-4">Revenue Trend</h3>
                <canvas id="revenueChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Platform performance chart
        const platformCtx = document.getElementById('platformChart').getContext('2d');
        new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: {{ data.affiliate_performance.performance_by_medium | map(attribute='medium') | list | tojson }},
                datasets: [{
                    data: {{ data.affiliate_performance.performance_by_medium | map(attribute='revenue') | list | tojson }},
                    backgroundColor: ['#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#3B82F6']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Revenue trend chart (placeholder data)
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Revenue',
                    data: [120, 190, 300, 500, 200, 300, 450],
                    borderColor: '#8B5CF6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        function viewCampaign(campaignId) {
            window.location.href = `/campaigns?id=${campaignId}`;
        }

        function generateQuickLink() {
            // Show modal or redirect to affiliate link generator
            window.location.href = '/affiliate-links';
        }

        // Auto-refresh performance metrics every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/performance-metrics');
                const data = await response.json();
                // Update dashboard metrics
                console.log('Updated metrics:', data);
            } catch (error) {
                console.error('Failed to update metrics:', error);
            }
        }, 30000);
    </script>
</body>
</html>
    '''
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    # Create campaign creation template
    create_campaign_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Campaign - Marketing Automation</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <nav class="bg-purple-600 text-white p-4">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">Marketing Automation</h1>
            <div class="space-x-4">
                <a href="/" class="hover:underline">Dashboard</a>
                <a href="/campaigns" class="hover:underline">Campaigns</a>
                <a href="/affiliate-links" class="hover:underline">Affiliate Links</a>
                <a href="/analytics" class="hover:underline">Analytics</a>
            </div>
        </div>
    </nav>

    <div class="container mx-auto p-6">
        <h2 class="text-3xl font-bold mb-6">Create New Campaign</h2>
        
        <div class="bg-white rounded-lg shadow p-6">
            <form id="campaignForm" class="space-y-6">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Campaign Name</label>
                    <input type="text" id="campaignName" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                           placeholder="e.g., Qahwa Coffee Holiday Campaign">
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Select Products</label>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {% for product in products %}
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" name="products" value="{{ product }}" 
                                   class="rounded border-gray-300 text-purple-600 focus:ring-purple-500">
                            <span class="text-sm">{{ product.replace('_', ' ').title() }}</span>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Select Platforms</label>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {% for platform in platforms %}
                        <label class="flex items-center space-x-2">
                            <input type="checkbox" name="platforms" value="{{ platform }}" 
                                   class="rounded border-gray-300 text-purple-600 focus:ring-purple-500">
                            <span class="text-sm">{{ platform.title() }}</span>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Campaign Duration (days)</label>
                        <input type="number" id="duration" value="7" min="1" max="365"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Budget ($)</label>
                        <input type="number" id="budget" value="500" min="0" step="0.01"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500">
                    </div>
                </div>

                <div class="flex space-x-4">
                    <button type="submit" 
                            class="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500">
                        Create Campaign
                    </button>
                    <button type="button" onclick="createAndLaunch()" 
                            class="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
                        Create & Launch Now
                    </button>
                    <a href="/campaigns" 
                       class="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500">
                        Cancel
                    </a>
                </div>
            </form>
        </div>
    </div>

    <script>
        document.getElementById('campaignForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await createCampaign(false);
        });

        async function createCampaign(launch = false) {
            const formData = new FormData(document.getElementById('campaignForm'));
            
            const data = {
                name: document.getElementById('campaignName').value,
                products: Array.from(document.querySelectorAll('input[name="products"]:checked')).map(cb => cb.value),
                platforms: Array.from(document.querySelectorAll('input[name="platforms"]:checked')).map(cb => cb.value),
                duration_days: parseInt(document.getElementById('duration').value),
                budget: parseFloat(document.getElementById('budget').value)
            };

            if (data.products.length === 0) {
                alert('Please select at least one product');
                return;
            }

            if (data.platforms.length === 0) {
                alert('Please select at least one platform');
                return;
            }

            try {
                const response = await fetch('/create-campaign', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    if (launch) {
                        // Launch immediately
                        const launchResponse = await fetch(`/launch-campaign/${result.campaign_id}`, {
                            method: 'POST'
                        });
                        const launchResult = await launchResponse.json();
                        
                        if (launchResult.success) {
                            alert(`Campaign created and launched! Success rate: ${launchResult.results.success_rate.toFixed(1)}%`);
                        } else {
                            alert(`Campaign created but launch failed: ${launchResult.message}`);
                        }
                    } else {
                        alert('Campaign created successfully!');
                    }
                    
                    window.location.href = '/campaigns';
                } else {
                    alert(`Failed to create campaign: ${result.message}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }

        async function createAndLaunch() {
            await createCampaign(true);
        }
    </script>
</body>
</html>
    '''
    
    with open('templates/create_campaign.html', 'w') as f:
        f.write(create_campaign_html)

if __name__ == '__main__':
    # Create HTML templates
    create_html_templates()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

