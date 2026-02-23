"""
Website Auditor Agent
Analyzes websites for issues and generates audit reports
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import time
import os


class SiteAuditor:
    """Crawls and analyzes websites for common issues"""
    
    # Red flags that indicate outdated tech
    OUTDATED_PATTERNS = [
        (r'jquery[.-]1\.[0-9]', 'jQuery 1.x (outdated)'),
        (r'bootstrap[.-][23]\.', 'Bootstrap 2/3 (outdated)'),
        (r'<table.*?width=', 'Table-based layout'),
        (r'<font\s', 'Font tags (HTML4)'),
        (r'<center>', 'Center tags (deprecated)'),
        (r'<marquee>', 'Marquee (deprecated)'),
        (r'flash\.js|swfobject', 'Flash content'),
        (r'Copyright\s*©?\s*(19[89]\d|200\d|201[0-5])', 'Old copyright year'),
    ]
    
    # Mobile-unfriendly indicators
    MOBILE_ISSUES = [
        (r'width\s*[=:]\s*["\']?\d{3,4}px', 'Fixed pixel widths'),
        (r'<meta[^>]+viewport', None),  # Absence is the issue
    ]
    
    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def audit_site(self, url: str) -> Dict[str, Any]:
        """Run full audit on a website"""
        
        # Normalize URL
        if not url.startswith('http'):
            url = f'https://{url}'
        
        domain = urlparse(url).netloc
        
        audit = {
            'url': url,
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'reachable': False,
            'ssl_valid': False,
            'load_time_ms': 0,
            'issues': [],
            'score': 100,  # Start at 100, deduct points
            'industry_hints': [],
            'tech_stack': [],
            'recommendation': '',
        }
        
        try:
            # Test HTTPS first
            audit.update(await self._check_ssl(url))
            
            # Fetch the homepage
            start = time.time()
            response = await self.session.get(url)
            audit['load_time_ms'] = int((time.time() - start) * 1000)
            audit['reachable'] = True
            audit['status_code'] = response.status_code
            
            html = response.text
            
            # Run all checks
            audit['issues'].extend(await self._check_outdated_tech(html))
            audit['issues'].extend(await self._check_mobile_friendly(html))
            audit['issues'].extend(await self._check_broken_links(url, html))
            audit['issues'].extend(await self._check_performance(response, audit['load_time_ms']))
            audit['issues'].extend(await self._check_seo(html, url))
            
            # Detect industry from content
            audit['industry_hints'] = await self._detect_industry(html)
            
            # Detect tech stack
            audit['tech_stack'] = await self._detect_tech_stack(html, response.headers)
            
            # Calculate score
            audit['score'] = self._calculate_score(audit['issues'])
            
            # Generate recommendation
            audit['recommendation'] = self._generate_recommendation(audit)
            
        except httpx.ConnectError:
            audit['issues'].append({
                'type': 'critical',
                'category': 'availability',
                'message': 'Website unreachable - connection failed',
                'points': -30
            })
            audit['score'] = 0
        except httpx.TimeoutException:
            audit['issues'].append({
                'type': 'critical', 
                'category': 'performance',
                'message': 'Website timed out (>15 seconds)',
                'points': -25
            })
            audit['score'] = 10
        except Exception as e:
            audit['issues'].append({
                'type': 'error',
                'category': 'unknown',
                'message': f'Audit error: {str(e)[:100]}',
                'points': -10
            })
        
        return audit
    
    async def _check_ssl(self, url: str) -> Dict[str, Any]:
        """Check SSL certificate validity"""
        result = {'ssl_valid': False, 'ssl_issues': []}
        
        try:
            https_url = url.replace('http://', 'https://')
            await self.session.head(https_url)
            result['ssl_valid'] = True
        except Exception:
            result['ssl_issues'].append({
                'type': 'critical',
                'category': 'security',
                'message': 'No valid SSL certificate - site not secure',
                'points': -20
            })
        
        return result
    
    async def _check_outdated_tech(self, html: str) -> List[Dict]:
        """Check for outdated technology patterns"""
        issues = []
        html_lower = html.lower()
        
        for pattern, description in self.OUTDATED_PATTERNS:
            if re.search(pattern, html_lower):
                issues.append({
                    'type': 'warning',
                    'category': 'technology',
                    'message': f'Outdated tech detected: {description}',
                    'points': -5
                })
        
        return issues
    
    async def _check_mobile_friendly(self, html: str) -> List[Dict]:
        """Check mobile responsiveness indicators"""
        issues = []
        
        # Check for viewport meta tag
        if not re.search(r'<meta[^>]+viewport', html, re.I):
            issues.append({
                'type': 'critical',
                'category': 'mobile',
                'message': 'No viewport meta tag - not mobile optimized',
                'points': -15
            })
        
        # Check for fixed widths
        fixed_widths = re.findall(r'width\s*[=:]\s*["\']?(\d{3,4})px', html)
        if len(fixed_widths) > 5:
            issues.append({
                'type': 'warning',
                'category': 'mobile',
                'message': f'Multiple fixed pixel widths ({len(fixed_widths)} found) - poor mobile experience',
                'points': -10
            })
        
        return issues
    
    async def _check_broken_links(self, base_url: str, html: str, max_check: int = 10) -> List[Dict]:
        """Check for broken internal links"""
        issues = []
        
        # Find all links
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        internal_links = []
        
        for link in links:
            if link.startswith('/') or base_url in link:
                full_url = urljoin(base_url, link)
                if full_url not in internal_links:
                    internal_links.append(full_url)
        
        # Check first N internal links
        broken = 0
        checked = 0
        
        for link in internal_links[:max_check]:
            try:
                resp = await self.session.head(link)
                if resp.status_code >= 400:
                    broken += 1
                checked += 1
            except:
                broken += 1
                checked += 1
        
        if broken > 0:
            issues.append({
                'type': 'warning',
                'category': 'links',
                'message': f'{broken} broken links found (checked {checked})',
                'points': -5 * broken
            })
        
        return issues
    
    async def _check_performance(self, response: httpx.Response, load_time: int) -> List[Dict]:
        """Check performance indicators"""
        issues = []
        
        # Load time
        if load_time > 5000:
            issues.append({
                'type': 'critical',
                'category': 'performance',
                'message': f'Very slow load time: {load_time/1000:.1f}s',
                'points': -15
            })
        elif load_time > 3000:
            issues.append({
                'type': 'warning',
                'category': 'performance',
                'message': f'Slow load time: {load_time/1000:.1f}s',
                'points': -8
            })
        
        # Page size
        content_length = len(response.content)
        if content_length > 2_000_000:  # 2MB
            issues.append({
                'type': 'warning',
                'category': 'performance',
                'message': f'Large page size: {content_length/1_000_000:.1f}MB',
                'points': -5
            })
        
        return issues
    
    async def _check_seo(self, html: str, url: str) -> List[Dict]:
        """Check basic SEO issues"""
        issues = []
        
        # Title tag
        if not re.search(r'<title[^>]*>.+</title>', html, re.I | re.S):
            issues.append({
                'type': 'warning',
                'category': 'seo',
                'message': 'Missing or empty title tag',
                'points': -5
            })
        
        # Meta description
        if not re.search(r'<meta[^>]+name=["\']description["\']', html, re.I):
            issues.append({
                'type': 'info',
                'category': 'seo',
                'message': 'Missing meta description',
                'points': -3
            })
        
        # H1 tag
        if not re.search(r'<h1[^>]*>', html, re.I):
            issues.append({
                'type': 'info',
                'category': 'seo',
                'message': 'Missing H1 heading',
                'points': -2
            })
        
        return issues
    
    async def _detect_industry(self, html: str) -> List[str]:
        """Detect likely industry from page content"""
        industries = []
        html_lower = html.lower()
        
        industry_keywords = {
            'legal': ['attorney', 'lawyer', 'law firm', 'legal', 'litigation'],
            'healthcare': ['medical', 'doctor', 'clinic', 'healthcare', 'patient', 'dental'],
            'real_estate': ['realtor', 'real estate', 'property', 'homes for sale', 'mortgage'],
            'restaurant': ['menu', 'restaurant', 'dining', 'cuisine', 'reservation'],
            'retail': ['shop', 'store', 'buy now', 'add to cart', 'products'],
            'construction': ['contractor', 'construction', 'roofing', 'plumbing', 'hvac'],
            'automotive': ['auto', 'car', 'vehicle', 'dealership', 'repair'],
            'finance': ['bank', 'loan', 'insurance', 'financial', 'investment'],
            'education': ['school', 'university', 'training', 'courses', 'education'],
            'technology': ['software', 'tech', 'digital', 'cloud', 'saas'],
        }
        
        for industry, keywords in industry_keywords.items():
            matches = sum(1 for kw in keywords if kw in html_lower)
            if matches >= 2:
                industries.append(industry)
        
        return industries or ['general']
    
    async def _detect_tech_stack(self, html: str, headers: httpx.Headers) -> List[str]:
        """Detect technology stack"""
        tech = []
        html_lower = html.lower()
        
        # CMS detection
        if 'wp-content' in html_lower:
            tech.append('WordPress')
        elif 'wix.com' in html_lower:
            tech.append('Wix')
        elif 'squarespace' in html_lower:
            tech.append('Squarespace')
        elif 'shopify' in html_lower:
            tech.append('Shopify')
        
        # Framework detection
        if 'react' in html_lower or '_next' in html_lower:
            tech.append('React')
        elif 'angular' in html_lower:
            tech.append('Angular')
        elif 'vue' in html_lower:
            tech.append('Vue.js')
        
        # Server detection
        server = headers.get('server', '').lower()
        if 'nginx' in server:
            tech.append('Nginx')
        elif 'apache' in server:
            tech.append('Apache')
        
        return tech
    
    def _calculate_score(self, issues: List[Dict]) -> int:
        """Calculate overall score from issues"""
        score = 100
        for issue in issues:
            score += issue.get('points', 0)
        return max(0, min(100, score))
    
    def _generate_recommendation(self, audit: Dict) -> str:
        """Generate a recommendation based on audit results"""
        score = audit['score']
        issues = audit['issues']
        
        critical = [i for i in issues if i['type'] == 'critical']
        
        if score < 30:
            return "This website needs a complete rebuild. It has critical issues affecting security, performance, and user experience."
        elif score < 50:
            return "This website has significant issues that are likely costing you customers. A modern redesign would greatly improve conversions."
        elif score < 70:
            return "Your website has room for improvement. Several issues could be hurting your search rankings and mobile users."
        elif score < 85:
            return "Your website is decent but could benefit from some updates to stay competitive."
        else:
            return "Your website is in good shape! Only minor optimizations recommended."
    
    async def close(self):
        await self.session.aclose()


async def audit_from_email(email: str) -> Dict[str, Any]:
    """Extract domain from email and audit the website"""
    domain = email.split('@')[-1]
    
    auditor = SiteAuditor()
    result = await auditor.audit_site(domain)
    result['source_email'] = email
    await auditor.close()
    
    return result


# Test
if __name__ == "__main__":
    async def test():
        auditor = SiteAuditor()
        
        # Test with a few sites
        test_sites = [
            "example.com",
            "google.com",
        ]
        
        for site in test_sites:
            print(f"\n{'='*60}")
            print(f"Auditing: {site}")
            print('='*60)
            
            result = await auditor.audit_site(site)
            
            print(f"Score: {result['score']}/100")
            print(f"Load time: {result['load_time_ms']}ms")
            print(f"SSL Valid: {result['ssl_valid']}")
            print(f"Industry: {result['industry_hints']}")
            print(f"Tech Stack: {result['tech_stack']}")
            print(f"\nIssues ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"  [{issue['type'].upper()}] {issue['message']}")
            print(f"\nRecommendation: {result['recommendation']}")
        
        await auditor.close()
    
    asyncio.run(test())
