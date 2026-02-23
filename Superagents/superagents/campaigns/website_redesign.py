"""
Website Redesign Campaign
- Imports emails from CSV
- Audits each website
- Matches to industry template
- Sends personalized email with expiring mockup link
"""

import asyncio
import csv
import os
import hashlib
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

import httpx
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Import our modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agents.site_auditor import SiteAuditor


class ExpiringLinkGenerator:
    """Generate time-limited preview links using signed tokens"""
    
    def __init__(self, secret_key: str = None, base_url: str = None):
        self.secret = secret_key or os.getenv("LINK_SECRET", "superagent-secret-2026")
        self.base_url = base_url or os.getenv("MOCKUP_BASE_URL", "https://yur-ai.com/preview")
    
    def generate_link(self, 
                      email: str, 
                      industry: str, 
                      template_id: str,
                      expires_minutes: int = 30) -> str:
        """Generate an expiring preview link"""
        
        expires_at = int(time.time()) + (expires_minutes * 60)
        
        # Create payload
        payload = f"{email}|{industry}|{template_id}|{expires_at}"
        
        # Sign it
        signature = hashlib.sha256(
            f"{payload}|{self.secret}".encode()
        ).hexdigest()[:16]
        
        # Encode for URL
        import base64
        token = base64.urlsafe_b64encode(
            f"{payload}|{signature}".encode()
        ).decode()
        
        return f"{self.base_url}?token={token}"
    
    def verify_link(self, token: str) -> Optional[Dict]:
        """Verify and decode an expiring link"""
        try:
            import base64
            decoded = base64.urlsafe_b64decode(token).decode()
            parts = decoded.split("|")
            
            if len(parts) != 5:
                return None
            
            email, industry, template_id, expires_at, signature = parts
            
            # Verify signature
            payload = f"{email}|{industry}|{template_id}|{expires_at}"
            expected_sig = hashlib.sha256(
                f"{payload}|{self.secret}".encode()
            ).hexdigest()[:16]
            
            if signature != expected_sig:
                return None
            
            # Check expiry
            if int(expires_at) < time.time():
                return {"expired": True, "email": email}
            
            return {
                "valid": True,
                "email": email,
                "industry": industry,
                "template_id": template_id,
                "expires_at": datetime.fromtimestamp(int(expires_at)).isoformat()
            }
            
        except Exception as e:
            return None


class WebsiteRedesignCampaign:
    """Run website redesign outreach campaign"""
    
    # Industry-specific mockup templates (10 per industry)
    INDUSTRY_TEMPLATES = {
        "legal": [
            "law-firm-modern-01", "law-firm-corporate-02", "attorney-boutique-03",
            "legal-practice-04", "law-dark-professional-05", "legal-light-clean-06",
            "attorney-gold-accent-07", "law-minimal-08", "legal-traditional-09", "law-tech-10"
        ],
        "healthcare": [
            "clinic-bright-01", "medical-professional-02", "dental-friendly-03",
            "healthcare-modern-04", "doctor-clean-05", "medical-trust-06",
            "clinic-blue-07", "healthcare-green-08", "medical-minimal-09", "clinic-warm-10"
        ],
        "real_estate": [
            "realtor-luxury-01", "realestate-modern-02", "property-clean-03",
            "homes-professional-04", "realtor-dark-05", "property-gallery-06",
            "realestate-search-07", "realtor-minimal-08", "homes-warm-09", "property-bold-10"
        ],
        "restaurant": [
            "restaurant-elegant-01", "cafe-modern-02", "dining-warm-03",
            "bistro-rustic-04", "restaurant-dark-05", "food-vibrant-06",
            "eatery-minimal-07", "restaurant-gallery-08", "dining-classic-09", "cafe-cozy-10"
        ],
        "construction": [
            "contractor-bold-01", "construction-industrial-02", "builder-modern-03",
            "trades-professional-04", "construction-dark-05", "contractor-clean-06",
            "build-minimal-07", "construction-orange-08", "trades-trust-09", "builder-tech-10"
        ],
        "automotive": [
            "auto-dealer-01", "car-modern-02", "automotive-dark-03",
            "dealer-gallery-04", "auto-professional-05", "car-minimal-06",
            "automotive-bold-07", "dealer-tech-08", "auto-luxury-09", "car-classic-10"
        ],
        "finance": [
            "finance-trust-01", "bank-modern-02", "investment-professional-03",
            "finance-dark-04", "bank-clean-05", "wealth-elegant-06",
            "finance-minimal-07", "bank-tech-08", "investment-bold-09", "finance-classic-10"
        ],
        "general": [
            "business-modern-01", "company-professional-02", "corporate-clean-03",
            "business-minimal-04", "company-bold-05", "corporate-tech-06",
            "business-elegant-07", "company-dark-08", "corporate-light-09", "business-gallery-10"
        ],
    }
    
    # Email template
    EMAIL_SUBJECT_TEMPLATES = [
        "I made a mockup of your new {company} website",
        "{first_name}, your site could look like this",
        "Quick question about {company}'s website",
        "30-minute website refresh for {company}?",
    ]
    
    def __init__(self):
        self.auditor = SiteAuditor()
        self.link_generator = ExpiringLinkGenerator()
        self.sendgrid = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        self.from_email = os.getenv("FROM_EMAIL", "roosevelt@yur-ai.com")
        self.from_name = os.getenv("FROM_NAME", "Roosevelt Franklin Technologies")
        
        # Results tracking
        self.results = {
            "total": 0,
            "audited": 0,
            "emailed": 0,
            "skipped": 0,
            "errors": []
        }
    
    async def load_emails_from_csv(self, filepath: str) -> List[Dict]:
        """Load email list from CSV file"""
        emails = []
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try common column names
                email = row.get('email') or row.get('Email') or row.get('EMAIL') or row.get('e-mail')
                company = row.get('company') or row.get('Company') or row.get('COMPANY') or ''
                name = row.get('name') or row.get('Name') or row.get('contact') or ''
                industry = row.get('industry') or row.get('Industry') or ''
                
                if email and '@' in email:
                    emails.append({
                        'email': email.strip(),
                        'company': company.strip(),
                        'name': name.strip(),
                        'industry': industry.strip().lower(),
                    })
        
        return emails
    
    async def process_lead(self, lead: Dict) -> Dict:
        """Process a single lead: audit site → generate mockup → send email"""
        
        email = lead['email']
        domain = email.split('@')[-1]
        
        result = {
            'email': email,
            'domain': domain,
            'status': 'pending',
            'audit_score': None,
            'industry': None,
            'emailed': False,
        }
        
        try:
            # Step 1: Audit the website
            audit = await self.auditor.audit_site(domain)
            result['audit_score'] = audit['score']
            result['issues_count'] = len(audit['issues'])
            
            # Skip if site is unreachable or already good
            if audit['score'] == 0:
                result['status'] = 'skipped_unreachable'
                self.results['skipped'] += 1
                return result
            
            if audit['score'] > 85:
                result['status'] = 'skipped_good_site'
                self.results['skipped'] += 1
                return result
            
            self.results['audited'] += 1
            
            # Step 2: Determine industry
            industry = lead.get('industry') or (audit['industry_hints'][0] if audit['industry_hints'] else 'general')
            result['industry'] = industry
            
            # Step 3: Pick a template
            templates = self.INDUSTRY_TEMPLATES.get(industry, self.INDUSTRY_TEMPLATES['general'])
            template_id = templates[hash(email) % len(templates)]  # Deterministic but varied
            
            # Step 4: Generate expiring link
            preview_link = self.link_generator.generate_link(
                email=email,
                industry=industry,
                template_id=template_id,
                expires_minutes=30
            )
            
            # Step 5: Build and send email
            email_sent = await self._send_redesign_email(
                to_email=email,
                to_name=lead.get('name', ''),
                company=lead.get('company') or domain,
                audit=audit,
                preview_link=preview_link,
                industry=industry,
            )
            
            if email_sent:
                result['status'] = 'emailed'
                result['emailed'] = True
                self.results['emailed'] += 1
            else:
                result['status'] = 'email_failed'
            
        except Exception as e:
            result['status'] = f'error: {str(e)[:50]}'
            self.results['errors'].append(f"{email}: {str(e)}")
        
        return result
    
    async def _send_redesign_email(self,
                                   to_email: str,
                                   to_name: str,
                                   company: str,
                                   audit: Dict,
                                   preview_link: str,
                                   industry: str) -> bool:
        """Send the website redesign pitch email"""
        
        # Parse name
        first_name = to_name.split()[0] if to_name else "there"
        
        # Pick subject line
        import random
        subject = random.choice(self.EMAIL_SUBJECT_TEMPLATES).format(
            company=company,
            first_name=first_name
        )
        
        # Build issue summary
        critical_issues = [i for i in audit['issues'] if i['type'] == 'critical']
        warning_issues = [i for i in audit['issues'] if i['type'] == 'warning']
        
        issue_bullets = ""
        for issue in (critical_issues + warning_issues)[:4]:
            issue_bullets += f"• {issue['message']}\n"
        
        # Build email body
        body = f"""Hi {first_name},

I was researching {industry} companies in Texas and came across {company}'s website.

I ran a quick audit and found a few things that might be hurting your online presence:

{issue_bullets}
Your site scored {audit['score']}/100 on our website health check.

I actually put together a quick mockup of what a modern refresh could look like for {company}. It takes 30 seconds to view:

👉 {preview_link}

(This preview link expires in 30 minutes – wanted to make sure you see it first)

If you like what you see, just reply to this email and we can chat. No pressure, no sales pitch – just wanted to show you what's possible.

Best,
{self.from_name}

P.S. – If you're not the right person for this, feel free to forward to whoever handles your website. Thanks!
"""
        
        # Send via SendGrid
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email, to_name),
                subject=subject,
                plain_text_content=Content("text/plain", body)
            )
            
            response = self.sendgrid.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"[ERROR] Email send failed: {e}")
            return False
    
    async def run_campaign(self, 
                           csv_path: str, 
                           limit: int = None,
                           dry_run: bool = False) -> Dict:
        """Run the full campaign"""
        
        print(f"\n{'='*60}")
        print("Website Redesign Campaign")
        print(f"{'='*60}")
        
        # Load emails
        leads = await self.load_emails_from_csv(csv_path)
        self.results['total'] = len(leads)
        print(f"Loaded {len(leads)} emails from {csv_path}")
        
        if limit:
            leads = leads[:limit]
            print(f"Processing first {limit} leads")
        
        if dry_run:
            print("[DRY RUN MODE - No emails will be sent]")
        
        # Process each lead
        for i, lead in enumerate(leads):
            print(f"\n[{i+1}/{len(leads)}] Processing {lead['email']}...", end=" ")
            
            if dry_run:
                # Just audit, don't send
                domain = lead['email'].split('@')[-1]
                audit = await self.auditor.audit_site(domain)
                print(f"Score: {audit['score']}/100", end=" ")
                if audit['score'] <= 85:
                    print("✓ Would email")
                    self.results['audited'] += 1
                else:
                    print("- Skipped (good site)")
                    self.results['skipped'] += 1
            else:
                result = await self.process_lead(lead)
                print(f"→ {result['status']}")
            
            # Rate limit
            await asyncio.sleep(1)  # 1 second between requests
        
        # Summary
        print(f"\n{'='*60}")
        print("Campaign Summary")
        print(f"{'='*60}")
        print(f"Total leads: {self.results['total']}")
        print(f"Sites audited: {self.results['audited']}")
        print(f"Emails sent: {self.results['emailed']}")
        print(f"Skipped: {self.results['skipped']}")
        print(f"Errors: {len(self.results['errors'])}")
        
        await self.auditor.close()
        
        return self.results
    
    async def close(self):
        await self.auditor.close()


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Website Redesign Campaign")
    parser.add_argument("csv", help="Path to CSV file with emails")
    parser.add_argument("--limit", type=int, help="Limit number of leads to process")
    parser.add_argument("--dry-run", action="store_true", help="Audit only, don't send emails")
    
    args = parser.parse_args()
    
    async def main():
        campaign = WebsiteRedesignCampaign()
        await campaign.run_campaign(
            csv_path=args.csv,
            limit=args.limit,
            dry_run=args.dry_run
        )
    
    asyncio.run(main())
