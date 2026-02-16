#!/usr/bin/env python3
"""
Marketing Automation System - Affiliate Link Generator
Automatically generates and tracks affiliate links without relying on APIs
"""

import json
import datetime
import sqlite3
import hashlib
import urllib.parse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AffiliateLink:
    """Represents a generated affiliate link"""
    link_id: str
    product_name: str
    product_id: str
    base_url: str
    affiliate_url: str
    tracking_code: str
    campaign: str
    medium: str
    source: str
    created_at: datetime.datetime
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0

@dataclass
class Product:
    """Product information for affiliate marketing"""
    product_id: str
    name: str
    description: str
    price: float
    category: str
    image_url: str
    base_url: str
    commission_rate: float
    keywords: List[str]
    target_audience: List[str]

class AffiliateLinkGenerator:
    """Generates and manages affiliate links automatically"""
    
    def __init__(self, db_path: str = "affiliate_links.db"):
        self.db_path = db_path
        self.init_database()
        self.load_products()
        
    def init_database(self):
        """Initialize SQLite database for affiliate link tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Affiliate links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_links (
                link_id TEXT PRIMARY KEY,
                product_name TEXT,
                product_id TEXT,
                base_url TEXT,
                affiliate_url TEXT,
                tracking_code TEXT,
                campaign TEXT,
                medium TEXT,
                source TEXT,
                created_at DATETIME,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0
            )
        ''')
        
        # Click tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                referrer TEXT,
                converted BOOLEAN DEFAULT FALSE,
                conversion_value REAL DEFAULT 0.0,
                FOREIGN KEY (link_id) REFERENCES affiliate_links (link_id)
            )
        ''')
        
        # Campaign performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign TEXT,
                date DATE,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                cost REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_products(self):
        """Load product catalog for affiliate marketing"""
        self.products = {
            # Qahwa Coffee Products
            "qahwa_falak_focus": Product(
                product_id="qahwa_falak_focus",
                name="Falak Focus Blend - Lion's Mane Coffee",
                description="Bold Arabic dark roast + Lion's Mane mushroom for enhanced focus and memory",
                price=24.99,
                category="functional_coffee",
                image_url="/images/falak-focus-blend.jpg",
                base_url="https://qahwacoffeebeans.com/products/falak-focus-blend",
                commission_rate=0.30,
                keywords=["lion's mane coffee", "focus coffee", "mushroom coffee", "arabic coffee", "nootropic coffee"],
                target_audience=["professionals", "students", "entrepreneurs", "biohackers"]
            ),
            
            "qahwa_miraj_mind": Product(
                product_id="qahwa_miraj_mind",
                name="Mi'raj Mind Roast - Cordyceps Energy",
                description="Light roast + Cordyceps mushroom for natural stamina and mental clarity",
                price=26.99,
                category="functional_coffee",
                image_url="/images/miraj-mind-roast.jpg",
                base_url="https://qahwacoffeebeans.com/products/miraj-mind-roast",
                commission_rate=0.30,
                keywords=["cordyceps coffee", "energy coffee", "pre-workout coffee", "natural energy", "stamina coffee"],
                target_audience=["athletes", "fitness enthusiasts", "busy professionals", "morning people"]
            ),
            
            "qahwa_anqa_immune": Product(
                product_id="qahwa_anqa_immune",
                name="Anqa Immune Shield - Reishi Coffee",
                description="Medium roast + Reishi & Turkey Tail mushrooms for immune support",
                price=28.99,
                category="functional_coffee",
                image_url="/images/anqa-immune-shield.jpg",
                base_url="https://qahwacoffeebeans.com/products/anqa-immune-shield",
                commission_rate=0.30,
                keywords=["reishi coffee", "immune coffee", "wellness coffee", "adaptogenic coffee", "health coffee"],
                target_audience=["health conscious", "wellness enthusiasts", "immune support seekers", "stress management"]
            ),
            
            # Digital Products
            "datascope_enhanced": Product(
                product_id="datascope_enhanced",
                name="DataScope Enhanced - Multi-Domain Intelligence Platform",
                description="Revolutionary data intelligence platform with cross-domain insights",
                price=99.00,
                category="software",
                image_url="/images/datascope-enhanced.jpg",
                base_url="https://meetaudreyevans.com/datascope-enhanced",
                commission_rate=0.50,
                keywords=["data intelligence", "business intelligence", "threat intelligence", "market analysis", "automation"],
                target_audience=["business owners", "analysts", "cybersecurity professionals", "real estate investors"]
            ),
            
            # Music & Creative
            "audrey_music_collection": Product(
                product_id="audrey_music_collection",
                name="Audrey Evans Music Collection",
                description="Original music collection with editing app access",
                price=19.99,
                category="music",
                image_url="/images/audrey-music-collection.jpg",
                base_url="https://meetaudreyevans.com/music",
                commission_rate=0.70,
                keywords=["original music", "music collection", "indie artist", "music editing", "creative tools"],
                target_audience=["music lovers", "content creators", "indie music fans", "creative professionals"]
            )
        }
    
    def generate_tracking_code(self, product_id: str, campaign: str, medium: str, source: str) -> str:
        """Generate unique tracking code for affiliate link"""
        timestamp = datetime.datetime.now().isoformat()
        raw_string = f"{product_id}_{campaign}_{medium}_{source}_{timestamp}"
        return hashlib.md5(raw_string.encode()).hexdigest()[:12]
    
    def create_affiliate_link(self, product_id: str, campaign: str = "general", 
                            medium: str = "social", source: str = "auto") -> AffiliateLink:
        """Create a new affiliate link with tracking"""
        
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} not found")
        
        product = self.products[product_id]
        tracking_code = self.generate_tracking_code(product_id, campaign, medium, source)
        
        # Build affiliate URL with UTM parameters
        utm_params = {
            'utm_source': source,
            'utm_medium': medium,
            'utm_campaign': campaign,
            'utm_content': product_id,
            'utm_term': tracking_code,
            'ref': 'audreyevans',
            'aff': tracking_code
        }
        
        # Add parameters to base URL
        parsed_url = urllib.parse.urlparse(product.base_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        query_params.update(utm_params)
        
        # Rebuild URL with tracking parameters
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        affiliate_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        link_id = f"aff_{tracking_code}"
        
        affiliate_link = AffiliateLink(
            link_id=link_id,
            product_name=product.name,
            product_id=product_id,
            base_url=product.base_url,
            affiliate_url=affiliate_url,
            tracking_code=tracking_code,
            campaign=campaign,
            medium=medium,
            source=source,
            created_at=datetime.datetime.now()
        )
        
        # Store in database
        self.store_affiliate_link(affiliate_link)
        
        return affiliate_link
    
    def store_affiliate_link(self, link: AffiliateLink):
        """Store affiliate link in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO affiliate_links 
            (link_id, product_name, product_id, base_url, affiliate_url, tracking_code,
             campaign, medium, source, created_at, clicks, conversions, revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            link.link_id, link.product_name, link.product_id, link.base_url,
            link.affiliate_url, link.tracking_code, link.campaign, link.medium,
            link.source, link.created_at, link.clicks, link.conversions, link.revenue
        ))
        
        conn.commit()
        conn.close()
    
    def generate_campaign_links(self, campaign_name: str, products: List[str] = None) -> Dict[str, AffiliateLink]:
        """Generate affiliate links for an entire campaign"""
        
        if products is None:
            products = list(self.products.keys())
        
        campaign_links = {}
        
        for product_id in products:
            if product_id in self.products:
                link = self.create_affiliate_link(
                    product_id=product_id,
                    campaign=campaign_name,
                    medium="social",
                    source="campaign_auto"
                )
                campaign_links[product_id] = link
        
        return campaign_links
    
    def generate_social_media_links(self, platform: str, post_type: str = "organic") -> Dict[str, AffiliateLink]:
        """Generate platform-specific affiliate links"""
        
        platform_configs = {
            "instagram": {"medium": "social", "source": "instagram"},
            "facebook": {"medium": "social", "source": "facebook"},
            "twitter": {"medium": "social", "source": "twitter"},
            "tiktok": {"medium": "video", "source": "tiktok"},
            "youtube": {"medium": "video", "source": "youtube"},
            "linkedin": {"medium": "professional", "source": "linkedin"},
            "pinterest": {"medium": "visual", "source": "pinterest"}
        }
        
        config = platform_configs.get(platform, {"medium": "social", "source": platform})
        
        links = {}
        for product_id in self.products.keys():
            campaign = f"{platform}_{post_type}_{datetime.datetime.now().strftime('%Y%m%d')}"
            
            link = self.create_affiliate_link(
                product_id=product_id,
                campaign=campaign,
                medium=config["medium"],
                source=config["source"]
            )
            links[product_id] = link
        
        return links
    
    def create_short_link(self, affiliate_link: AffiliateLink) -> str:
        """Create a shortened version of affiliate link"""
        # In production, you'd use a URL shortener service
        # For now, create a simple redirect system
        short_code = affiliate_link.tracking_code[:8]
        return f"https://meetaudreyevans.com/go/{short_code}"
    
    def track_click(self, link_id: str, ip_address: str = None, 
                   user_agent: str = None, referrer: str = None):
        """Track a click on an affiliate link"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Record the click
        cursor.execute('''
            INSERT INTO click_tracking 
            (link_id, ip_address, user_agent, referrer)
            VALUES (?, ?, ?, ?)
        ''', (link_id, ip_address, user_agent, referrer))
        
        # Update click count
        cursor.execute('''
            UPDATE affiliate_links 
            SET clicks = clicks + 1 
            WHERE link_id = ?
        ''', (link_id,))
        
        conn.commit()
        conn.close()
    
    def track_conversion(self, link_id: str, conversion_value: float):
        """Track a conversion from an affiliate link"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update the most recent click as converted
        cursor.execute('''
            UPDATE click_tracking 
            SET converted = TRUE, conversion_value = ?
            WHERE link_id = ? AND converted = FALSE
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (conversion_value, link_id))
        
        # Update affiliate link stats
        cursor.execute('''
            UPDATE affiliate_links 
            SET conversions = conversions + 1, revenue = revenue + ?
            WHERE link_id = ?
        ''', (conversion_value, link_id))
        
        conn.commit()
        conn.close()
    
    def get_link_performance(self, link_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific link"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM affiliate_links WHERE link_id = ?
        ''', (link_id,))
        
        link_data = cursor.fetchone()
        if not link_data:
            return None
        
        # Get detailed click data
        cursor.execute('''
            SELECT COUNT(*) as total_clicks,
                   COUNT(CASE WHEN converted = TRUE THEN 1 END) as conversions,
                   SUM(conversion_value) as total_revenue
            FROM click_tracking 
            WHERE link_id = ?
        ''', (link_id,))
        
        stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "link_id": link_data[0],
            "product_name": link_data[1],
            "affiliate_url": link_data[4],
            "campaign": link_data[6],
            "medium": link_data[7],
            "source": link_data[8],
            "created_at": link_data[9],
            "total_clicks": stats[0] or 0,
            "conversions": stats[1] or 0,
            "total_revenue": stats[2] or 0.0,
            "conversion_rate": (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
            "revenue_per_click": (stats[2] / stats[0]) if stats[0] > 0 else 0
        }
    
    def get_campaign_performance(self, campaign: str) -> Dict[str, Any]:
        """Get performance metrics for an entire campaign"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_links,
                SUM(clicks) as total_clicks,
                SUM(conversions) as total_conversions,
                SUM(revenue) as total_revenue
            FROM affiliate_links 
            WHERE campaign = ?
        ''', (campaign,))
        
        stats = cursor.fetchone()
        
        # Get top performing links in campaign
        cursor.execute('''
            SELECT link_id, product_name, clicks, conversions, revenue
            FROM affiliate_links 
            WHERE campaign = ?
            ORDER BY revenue DESC
            LIMIT 5
        ''', (campaign,))
        
        top_links = cursor.fetchall()
        
        conn.close()
        
        return {
            "campaign": campaign,
            "total_links": stats[0] or 0,
            "total_clicks": stats[1] or 0,
            "total_conversions": stats[2] or 0,
            "total_revenue": stats[3] or 0.0,
            "conversion_rate": (stats[2] / stats[1] * 100) if stats[1] > 0 else 0,
            "revenue_per_click": (stats[3] / stats[1]) if stats[1] > 0 else 0,
            "top_performing_links": [
                {
                    "link_id": link[0],
                    "product_name": link[1],
                    "clicks": link[2],
                    "conversions": link[3],
                    "revenue": link[4]
                } for link in top_links
            ]
        }
    
    def generate_link_report(self) -> Dict[str, Any]:
        """Generate comprehensive affiliate link performance report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_links,
                SUM(clicks) as total_clicks,
                SUM(conversions) as total_conversions,
                SUM(revenue) as total_revenue
            FROM affiliate_links
        ''')
        
        overall_stats = cursor.fetchone()
        
        # Performance by medium
        cursor.execute('''
            SELECT 
                medium,
                COUNT(*) as links,
                SUM(clicks) as clicks,
                SUM(conversions) as conversions,
                SUM(revenue) as revenue
            FROM affiliate_links
            GROUP BY medium
            ORDER BY revenue DESC
        ''')
        
        medium_performance = cursor.fetchall()
        
        # Performance by product
        cursor.execute('''
            SELECT 
                product_id,
                product_name,
                COUNT(*) as links,
                SUM(clicks) as clicks,
                SUM(conversions) as conversions,
                SUM(revenue) as revenue
            FROM affiliate_links
            GROUP BY product_id, product_name
            ORDER BY revenue DESC
        ''')
        
        product_performance = cursor.fetchall()
        
        conn.close()
        
        return {
            "report_generated_at": datetime.datetime.now().isoformat(),
            "overall_performance": {
                "total_links": overall_stats[0] or 0,
                "total_clicks": overall_stats[1] or 0,
                "total_conversions": overall_stats[2] or 0,
                "total_revenue": overall_stats[3] or 0.0,
                "overall_conversion_rate": (overall_stats[2] / overall_stats[1] * 100) if overall_stats[1] > 0 else 0
            },
            "performance_by_medium": [
                {
                    "medium": row[0],
                    "links": row[1],
                    "clicks": row[2],
                    "conversions": row[3],
                    "revenue": row[4],
                    "conversion_rate": (row[3] / row[2] * 100) if row[2] > 0 else 0
                } for row in medium_performance
            ],
            "performance_by_product": [
                {
                    "product_id": row[0],
                    "product_name": row[1],
                    "links": row[2],
                    "clicks": row[3],
                    "conversions": row[4],
                    "revenue": row[5],
                    "conversion_rate": (row[4] / row[3] * 100) if row[3] > 0 else 0
                } for row in product_performance
            ]
        }

def main():
    """Demo the affiliate link generator"""
    generator = AffiliateLinkGenerator()
    
    print("=== Affiliate Link Generator Demo ===")
    
    # Generate links for social media campaign
    instagram_links = generator.generate_social_media_links("instagram", "story")
    
    print(f"\nGenerated {len(instagram_links)} Instagram affiliate links:")
    for product_id, link in instagram_links.items():
        short_link = generator.create_short_link(link)
        print(f"• {link.product_name}")
        print(f"  Short Link: {short_link}")
        print(f"  Tracking: {link.tracking_code}")
        print()
    
    # Simulate some clicks and conversions
    for link in list(instagram_links.values())[:2]:
        generator.track_click(link.link_id, "192.168.1.1", "Mozilla/5.0", "instagram.com")
        if link.product_id == "qahwa_falak_focus":
            generator.track_conversion(link.link_id, 24.99)
    
    # Generate performance report
    report = generator.generate_link_report()
    
    print("=== Performance Report ===")
    print(f"Total Links: {report['overall_performance']['total_links']}")
    print(f"Total Clicks: {report['overall_performance']['total_clicks']}")
    print(f"Total Revenue: ${report['overall_performance']['total_revenue']:.2f}")
    print(f"Conversion Rate: {report['overall_performance']['overall_conversion_rate']:.2f}%")
    
    return report

if __name__ == "__main__":
    main()

