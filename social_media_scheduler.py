#!/usr/bin/env python3
"""
Marketing Automation Standalone - Social Media Scheduler
Blue Ocean Enhancement: Multi-platform scheduling, TikTok integration, email campaigns
"""

import json
import datetime
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScheduledPost:
    """A post scheduled for future publishing"""
    post_id: str
    platform: str
    content: str
    media_urls: List[str]
    hashtags: List[str]
    scheduled_time: str
    status: str = 'scheduled'  # scheduled, published, failed, cancelled
    affiliate_links: List[str] = field(default_factory=list)
    campaign_id: Optional[str] = None
    engagement: Dict[str, int] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class EmailCampaign:
    """An email marketing campaign"""
    campaign_id: str
    name: str
    subject: str
    body_html: str
    body_text: str
    recipient_list: str  # list name
    scheduled_time: str
    status: str = 'draft'
    sent_count: int = 0
    open_count: int = 0
    click_count: int = 0
    unsubscribe_count: int = 0


class SocialMediaScheduler:
    """Multi-platform social media scheduling with TikTok integration"""

    SUPPORTED_PLATFORMS = [
        'instagram', 'facebook', 'twitter', 'linkedin',
        'tiktok', 'pinterest', 'lemon8', 'youtube'
    ]

    TIKTOK_CONTENT_TYPES = [
        'short_video', 'photo_carousel', 'story', 'live_promo'
    ]

    def __init__(self, db_path: str = 'scheduler.db'):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the scheduler database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                post_id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                content TEXT,
                media_urls TEXT,
                hashtags TEXT,
                scheduled_time DATETIME,
                status TEXT DEFAULT 'scheduled',
                affiliate_links TEXT,
                campaign_id TEXT,
                engagement TEXT,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS email_campaigns (
                campaign_id TEXT PRIMARY KEY,
                name TEXT,
                subject TEXT,
                body_html TEXT,
                body_text TEXT,
                recipient_list TEXT,
                scheduled_time DATETIME,
                status TEXT DEFAULT 'draft',
                sent_count INTEGER DEFAULT 0,
                open_count INTEGER DEFAULT 0,
                click_count INTEGER DEFAULT 0,
                unsubscribe_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS content_calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                platform TEXT,
                content_type TEXT,
                topic TEXT,
                notes TEXT,
                post_id TEXT,
                status TEXT DEFAULT 'planned'
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS tiktok_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_name TEXT,
                hashtag TEXT,
                category TEXT,
                view_count INTEGER,
                discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_in_post TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def schedule_post(self, platform: str, content: str,
                      scheduled_time: str, media_urls: List[str] = None,
                      hashtags: List[str] = None,
                      affiliate_links: List[str] = None,
                      campaign_id: str = None) -> ScheduledPost:
        """Schedule a post for a specific platform and time"""

        post_id = f"post_{platform}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        post = ScheduledPost(
            post_id=post_id,
            platform=platform,
            content=content,
            media_urls=media_urls or [],
            hashtags=hashtags or [],
            scheduled_time=scheduled_time,
            affiliate_links=affiliate_links or [],
            campaign_id=campaign_id,
        )

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO scheduled_posts
            (post_id, platform, content, media_urls, hashtags, scheduled_time,
             status, affiliate_links, campaign_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.post_id, post.platform, post.content,
            json.dumps(post.media_urls), json.dumps(post.hashtags),
            post.scheduled_time, post.status,
            json.dumps(post.affiliate_links), post.campaign_id,
        ))
        conn.commit()
        conn.close()

        logger.info(f"Scheduled post {post_id} for {platform} at {scheduled_time}")
        return post

    def schedule_cross_platform(self, content: str, platforms: List[str],
                                scheduled_time: str, **kwargs) -> List[ScheduledPost]:
        """Schedule the same content across multiple platforms with platform-specific adjustments"""
        posts = []
        for platform in platforms:
            adapted = self._adapt_content_for_platform(content, platform)
            post = self.schedule_post(
                platform=platform,
                content=adapted,
                scheduled_time=scheduled_time,
                **kwargs,
            )
            posts.append(post)
        return posts

    def _adapt_content_for_platform(self, content: str, platform: str) -> str:
        """Adapt content for platform-specific requirements"""
        limits = {
            'twitter': 280,
            'instagram': 2200,
            'facebook': 63206,
            'linkedin': 3000,
            'tiktok': 2200,
            'pinterest': 500,
            'lemon8': 2000,
        }
        limit = limits.get(platform, 5000)
        if len(content) > limit:
            content = content[:limit - 3] + '...'
        return content

    def get_pending_posts(self) -> List[Dict[str, Any]]:
        """Get all posts that are due for publishing"""
        now = datetime.datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT * FROM scheduled_posts
            WHERE status = 'scheduled' AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
        ''', (now,))
        rows = c.fetchall()
        conn.close()
        return [self._row_to_post(r) for r in rows]

    def get_calendar(self, start_date: str, end_date: str) -> List[Dict]:
        """Get content calendar for a date range"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT * FROM content_calendar
            WHERE date BETWEEN ? AND ?
            ORDER BY date, platform
        ''', (start_date, end_date))
        rows = c.fetchall()
        conn.close()
        return [{'id': r[0], 'date': r[1], 'platform': r[2],
                 'content_type': r[3], 'topic': r[4], 'notes': r[5],
                 'post_id': r[6], 'status': r[7]} for r in rows]

    # ---- TikTok Integration (Blue Ocean) ----

    def create_tiktok_post(self, content: str, video_url: str,
                           hashtags: List[str] = None,
                           scheduled_time: str = None,
                           sound_id: str = None) -> ScheduledPost:
        """Create a TikTok-specific post with trending sounds and hashtags"""
        tiktok_hashtags = hashtags or []
        trends = self._get_tiktok_trends()
        for trend in trends[:3]:
            if trend['hashtag'] not in tiktok_hashtags:
                tiktok_hashtags.append(trend['hashtag'])

        scheduled = scheduled_time or (
            datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        ).isoformat()

        return self.schedule_post(
            platform='tiktok',
            content=content,
            media_urls=[video_url],
            hashtags=tiktok_hashtags,
            scheduled_time=scheduled,
        )

    def _get_tiktok_trends(self) -> List[Dict]:
        """Get current TikTok trending topics and sounds"""
        return [
            {'trend_name': 'Coffee Culture', 'hashtag': '#CoffeeTok',
             'category': 'Food & Drink', 'view_count': 15_000_000},
            {'trend_name': 'Small Business', 'hashtag': '#SmallBusinessCheck',
             'category': 'Business', 'view_count': 8_000_000},
            {'trend_name': 'Productivity', 'hashtag': '#ProductivityHacks',
             'category': 'Education', 'view_count': 12_000_000},
            {'trend_name': 'Mushroom Coffee', 'hashtag': '#MushroomCoffee',
             'category': 'Wellness', 'view_count': 5_000_000},
        ]

    # ---- Email Campaign Builder (Blue Ocean) ----

    def create_email_campaign(self, name: str, subject: str,
                              body_html: str, body_text: str,
                              recipient_list: str,
                              scheduled_time: str = None) -> EmailCampaign:
        """Create an email marketing campaign"""
        campaign_id = f"email_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        scheduled = scheduled_time or (
            datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        ).isoformat()

        campaign = EmailCampaign(
            campaign_id=campaign_id,
            name=name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            recipient_list=recipient_list,
            scheduled_time=scheduled,
        )

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO email_campaigns
            (campaign_id, name, subject, body_html, body_text,
             recipient_list, scheduled_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign.campaign_id, campaign.name, campaign.subject,
            campaign.body_html, campaign.body_text,
            campaign.recipient_list, campaign.scheduled_time, campaign.status,
        ))
        conn.commit()
        conn.close()

        logger.info(f"Created email campaign: {campaign_id}")
        return campaign

    def get_email_campaigns(self) -> List[Dict]:
        """Get all email campaigns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM email_campaigns ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        return [self._email_row_to_dict(r) for r in rows]

    def _row_to_post(self, row) -> Dict:
        """Convert a database row to a post dictionary"""
        return {
            'post_id': row[0], 'platform': row[1], 'content': row[2],
            'media_urls': json.loads(row[3]) if row[3] else [],
            'hashtags': json.loads(row[4]) if row[4] else [],
            'scheduled_time': row[5], 'status': row[6],
            'affiliate_links': json.loads(row[7]) if row[7] else [],
            'campaign_id': row[8],
        }

    def _email_row_to_dict(self, row) -> Dict:
        """Convert email campaign row to dictionary"""
        return {
            'campaign_id': row[0], 'name': row[1], 'subject': row[2],
            'body_html': row[3], 'body_text': row[4],
            'recipient_list': row[5], 'scheduled_time': row[6],
            'status': row[7], 'sent_count': row[8],
            'open_count': row[9], 'click_count': row[10],
            'unsubscribe_count': row[11],
        }
