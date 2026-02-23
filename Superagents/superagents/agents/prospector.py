"""
Lead Prospector Agent
Finds 30-50 qualified leads daily from Apollo.io
"""

import asyncio
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime
from core.trinity_client import TrinityClient
from core.config import SuperagentConfig
import os


class LinkedInProspector:
    """Autonomous lead prospecting agent using Apollo.io + Hunter.io"""
    
    APOLLO_BASE_URL = "https://api.apollo.io/api/v1"
    LINKEDIN_BASE_URL = "https://api.linkedin.com/v2"
    HUNTER_BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self):
        self.trinity = TrinityClient()
        self.session = httpx.AsyncClient(timeout=30.0)
        self.apollo_key = os.getenv("APOLLO_API_KEY", SuperagentConfig.APOLLO_API_KEY if hasattr(SuperagentConfig, 'APOLLO_API_KEY') else "")
        self.linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN", SuperagentConfig.LINKEDIN_ACCESS_TOKEN if hasattr(SuperagentConfig, 'LINKEDIN_ACCESS_TOKEN') else "")
        self.hunter_key = os.getenv("HUNTER_API_KEY", "")
        self.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.apollo_key,
        }
        self.linkedin_headers = {
            "Authorization": f"Bearer {self.linkedin_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
    
    async def find_prospects(self, 
                            industry: str = "fintech",
                            company_size: str = "20-500",
                            funding_min: int = 5,
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Find prospect companies matching criteria using Apollo.io"""
        
        # Parse company size range
        try:
            min_emp, max_emp = map(int, company_size.split("-"))
        except:
            min_emp, max_emp = 20, 500
        
        prospects = await self._search_apollo_companies(
            industry=industry,
            min_employees=min_emp,
            max_employees=max_emp,
            limit=limit
        )
        
        print(f"[INFO] Apollo found {len(prospects)} prospect companies")
        return prospects
    
    async def get_decision_makers(self, company_domain: str) -> List[Dict[str, Any]]:
        """Find decision-makers at a company using Hunter.io + LinkedIn fallback"""
        
        # First try Hunter.io for email finding (free tier: 25/mo)
        if self.hunter_key:
            makers = await self._search_hunter_domain(company_domain)
            if makers:
                print(f"[INFO] Found {len(makers)} contacts via Hunter.io at {company_domain}")
                return makers
        
        # Fallback to LinkedIn if we have a token (limited access)
        if self.linkedin_token:
            makers = await self._search_linkedin_by_company(company_domain)
            if makers:
                print(f"[INFO] Found {len(makers)} decision-makers via LinkedIn at {company_domain}")
                return makers
        
        # Last resort: Apollo (requires paid plan)
        decision_maker_titles = [
            "CEO", "CTO", "CFO", "COO",
            "Chief Financial Officer",
            "Chief Technology Officer",
            "VP Operations", 
            "VP Engineering",
            "VP Finance",
            "Director of Engineering",
            "Head of Technology",
        ]
        
        makers = await self._search_apollo_people(
            company_domain=company_domain,
            titles=decision_maker_titles,
            limit=5
        )
        
        print(f"[INFO] Found {len(makers)} decision-makers at {company_domain}")
        return makers
    
    async def _search_hunter_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Search Hunter.io for emails at a domain"""
        try:
            # Domain search - finds emails and people at a company
            response = await self.session.get(
                f"{self.HUNTER_BASE_URL}/domain-search",
                params={
                    "domain": domain,
                    "api_key": self.hunter_key,
                    "limit": 10,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                emails = data.get("data", {}).get("emails", [])
                
                # Filter for decision-maker roles
                decision_titles = ["ceo", "cto", "cfo", "coo", "founder", "director", "vp", "head", "chief"]
                
                contacts = []
                for email_data in emails:
                    position = (email_data.get("position") or "").lower()
                    # Include if decision-maker or no position filter
                    if not position or any(title in position for title in decision_titles):
                        contacts.append({
                            "id": email_data.get("email", ""),
                            "name": f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                            "first_name": email_data.get("first_name"),
                            "last_name": email_data.get("last_name"),
                            "title": email_data.get("position", ""),
                            "email": email_data.get("value"),
                            "confidence": email_data.get("confidence", 0),
                            "linkedin_url": email_data.get("linkedin"),
                            "company": domain,
                        })
                
                return contacts
            elif response.status_code == 401:
                print(f"[WARN] Hunter.io API key invalid")
                return []
            elif response.status_code == 429:
                print(f"[WARN] Hunter.io rate limit reached")
                return []
            else:
                print(f"[DEBUG] Hunter.io search status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] Hunter.io search error: {e}")
            return []
    
    async def _find_email_by_name(self, domain: str, first_name: str, last_name: str) -> Optional[str]:
        """Find specific person's email using Hunter.io email finder"""
        if not self.hunter_key:
            return None
            
        try:
            response = await self.session.get(
                f"{self.HUNTER_BASE_URL}/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": self.hunter_key,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("email")
            return None
            
        except Exception as e:
            print(f"[DEBUG] Hunter email finder error: {e}")
            return None
    
    async def _search_linkedin_by_company(self, company_domain: str) -> List[Dict[str, Any]]:
        """Search LinkedIn for people at a company by domain"""
        try:
            # First, find the company by domain/name
            company_info = await self._get_linkedin_company(company_domain)
            if not company_info:
                return []
            
            company_id = company_info.get("id")
            if not company_id:
                return []
            
            # Search for people at this company with leadership titles
            # LinkedIn API: /organizationalEntityAcls or /people search
            response = await self.session.get(
                f"{self.LINKEDIN_BASE_URL}/organizationAcls",
                params={
                    "q": "roleAssignee",
                    "projection": "(elements*(organizationalTarget,role))"
                },
                headers=self.linkedin_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract people from org acls
                people = []
                for elem in data.get("elements", []):
                    people.append({
                        "id": elem.get("id", ""),
                        "name": "",  # Will need enrichment
                        "title": elem.get("role", ""),
                        "email": "",  # LinkedIn doesn't expose emails directly
                        "linkedin_url": "",
                        "company": company_domain,
                    })
                return people
            else:
                print(f"[DEBUG] LinkedIn org search status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[WARN] LinkedIn company search error: {e}")
            return []
    
    async def _get_linkedin_company(self, domain: str) -> Optional[Dict[str, Any]]:
        """Look up a LinkedIn company by domain"""
        try:
            # Try to find company by vanity name (derived from domain)
            vanity_name = domain.split(".")[0]  # e.g., "google" from "google.com"
            
            response = await self.session.get(
                f"{self.LINKEDIN_BASE_URL}/organizations",
                params={
                    "q": "vanityName",
                    "vanityName": vanity_name
                },
                headers=self.linkedin_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                if elements:
                    return elements[0]
            
            return None
            
        except Exception as e:
            print(f"[DEBUG] LinkedIn company lookup error: {e}")
            return None
    
    async def enrich_prospect(self, 
                             prospect_id: str,
                             company_name: str) -> Dict[str, Any]:
        """Enrich prospect with company data"""
        
        enriched = {
            "company_id": prospect_id,
            "company_name": company_name,
            "recent_news": await self._get_recent_news(company_name),
            "funding_info": await self._get_funding_info(prospect_id),
            "company_size": await self._get_company_size(prospect_id),
            "technologies": await self._get_company_tech_stack(prospect_id),
        }
        
        return enriched
    
    async def create_lead_from_prospect(self,
                                       person_name: str,
                                       person_title: str,
                                       person_email: str,
                                       company_name: str,
                                       enrichment: Dict[str, Any]) -> Dict[str, Any]:
        """Create Trinity lead from prospect data"""
        
        lead = await self.trinity.create_lead(
            name=person_name,
            email=person_email,
            company=company_name,
            title=person_title,
            source="linkedin-prospector",
            metadata={
                "funding_info": enrichment.get("funding_info"),
                "recent_news": enrichment.get("recent_news"),
                "company_size": enrichment.get("company_size"),
                "technologies": enrichment.get("technologies"),
                "score": await self._calculate_fit_score(enrichment),
            }
        )
        
        return lead
    
    async def run_daily_prospecting(self) -> Dict[str, Any]:
        """Run full daily prospecting cycle"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "prospects_found": 0,
            "leads_created": 0,
            "errors": [],
        }
        
        try:
            # Find prospects
            prospects = await self.find_prospects(limit=50)
            results["prospects_found"] = len(prospects)
            
            # For each prospect, get decision-makers, enrich, and create leads
            for prospect in prospects[:SuperagentConfig.DAILY_MAX_EMAILS]:
                try:
                    # Get decision-makers using company domain
                    company_domain = prospect.get("domain", "")
                    if not company_domain:
                        continue
                        
                    makers = await self.get_decision_makers(company_domain)
                    
                    # Enrich company data
                    enrichment = await self.enrich_prospect(
                        prospect.get("id", ""),
                        prospect["name"]
                    )
                    
                    # Create Trinity leads
                    for maker in makers:
                        lead = await self.create_lead_from_prospect(
                            person_name=maker["name"],
                            person_title=maker["title"],
                            person_email=maker.get("email", ""),
                            company_name=prospect["name"],
                            enrichment=enrichment,
                        )
                        
                        if "id" in lead:
                            results["leads_created"] += 1
                            
                            # Trigger email sequence for new lead
                            await self.trinity.log_interaction(
                                lead_id=lead["id"],
                                interaction_type="lead_created",
                                content=f"Lead created from {prospect['name']}",
                                metadata={"source": "linkedin-prospector"}
                            )
                
                except Exception as e:
                    results["errors"].append(f"Error processing prospect {prospect.get('name')}: {str(e)}")
            
            print(f"[SUCCESS] Prospecting complete: {results['leads_created']} leads created")
            
        except Exception as e:
            results["errors"].append(f"Fatal error in prospecting: {str(e)}")
        
        return results
    
    # Helper methods - Apollo.io API implementations
    
    async def _search_apollo_companies(self, 
                                       industry: str,
                                       min_employees: int = 20,
                                       max_employees: int = 500,
                                       min_funding: int = 5_000_000,
                                       limit: int = 50) -> List[Dict[str, Any]]:
        """Search Apollo for companies matching criteria (free tier)"""
        try:
            payload = {
                "q_organization_keyword_tags": [industry],
                "organization_num_employees_ranges": [f"{min_employees},{max_employees}"],
                "per_page": min(limit, 25),
                "page": 1,
            }
            
            response = await self.session.post(
                f"{self.APOLLO_BASE_URL}/organizations/search",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                companies = data.get("organizations", [])
                print(f"[DEBUG] Apollo returned {len(companies)} companies")
                return [
                    {
                        "id": c.get("id"),
                        "name": c.get("name"),
                        "domain": c.get("primary_domain"),
                        "industry": c.get("industry"),
                        "employee_count": c.get("estimated_num_employees"),
                        "linkedin_url": c.get("linkedin_url"),
                        "founded_year": c.get("founded_year"),
                    }
                    for c in companies
                ]
            else:
                print(f"[WARN] Apollo company search failed: {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"[ERROR] Apollo company search error: {e}")
            return []
    
    async def _search_apollo_people(self, 
                                    company_domain: str = None,
                                    titles: List[str] = None,
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """Search Apollo for people (decision-makers) with emails.
        NOTE: People search requires Apollo paid plan. Returns empty on free tier."""
        try:
            payload = {
                "per_page": min(limit, 25),
                "page": 1,
            }
            
            if company_domain:
                payload["q_organization_domains"] = company_domain
            
            if titles:
                payload["person_titles"] = titles
            
            response = await self.session.post(
                f"{self.APOLLO_BASE_URL}/people/search",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                people = data.get("people", [])
                return [
                    {
                        "id": p.get("id"),
                        "name": f"{p.get('first_name', '')} {p.get('last_name', '')}".strip(),
                        "first_name": p.get("first_name"),
                        "last_name": p.get("last_name"),
                        "title": p.get("title"),
                        "email": p.get("email"),
                        "linkedin_url": p.get("linkedin_url"),
                        "company": p.get("organization", {}).get("name"),
                        "company_domain": p.get("organization", {}).get("primary_domain"),
                    }
                    for p in people
                    if p.get("email")  # Only include people with emails
                ]
            elif response.status_code == 403:
                # Free tier doesn't have people search - return placeholder
                print(f"[INFO] Apollo people search requires paid plan. Using company domain as placeholder.")
                return []
            else:
                print(f"[WARN] Apollo people search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[ERROR] Apollo people search error: {e}")
            return []
    
    async def _enrich_person(self, email: str) -> Optional[Dict[str, Any]]:
        """Enrich a person's data by email"""
        try:
            payload = {
                "email": email,
            }
            
            response = await self.session.post(
                f"{self.APOLLO_BASE_URL}/people/match",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get("person", {})
            return None
            
        except Exception as e:
            print(f"[ERROR] Apollo enrich error: {e}")
            return None

    async def _search_crunchbase(self, **kwargs) -> List[Dict[str, Any]]:
        """Search for companies - now uses Apollo"""
        return await self._search_apollo_companies(
            industry=kwargs.get("industry", "technology"),
            min_employees=20,
            max_employees=500,
            limit=kwargs.get("limit", 50)
        )
    
    async def _search_linkedin_people(self, **kwargs) -> List[Dict[str, Any]]:
        """Search for people - now uses Apollo"""
        company_id = kwargs.get("company_id", "")
        titles = kwargs.get("titles", [])
        
        # Apollo uses domain, not company_id, so we need to get the domain first
        return await self._search_apollo_people(
            company_domain=company_id,  # Assuming company_id is actually domain
            titles=titles,
            limit=10
        )
    
    async def _get_recent_news(self, company_name: str) -> List[str]:
        """Get recent company news"""
        # TODO: Implement news API integration
        return []
    
    async def _get_funding_info(self, company_id: str) -> Dict[str, Any]:
        """Get funding information"""
        # TODO: Implement Crunchbase funding API
        return {}
    
    async def _get_company_size(self, company_id: str) -> int:
        """Get company headcount"""
        # TODO: Implement LinkedIn company API
        return 0
    
    async def _get_company_tech_stack(self, company_id: str) -> List[str]:
        """Get company technology stack"""
        # TODO: Implement StackShare API integration
        return []
    
    async def _calculate_fit_score(self, enrichment: Dict[str, Any]) -> float:
        """Calculate lead quality score (0-100)"""
        score = 0.0
        
        # Funded companies score higher
        if enrichment.get("funding_info", {}).get("total_raised", 0) > 5_000_000:
            score += 25
        
        # Growing companies score higher
        if enrichment.get("company_size", 0) > 50:
            score += 20
        
        # Recent news is positive signal
        if enrichment.get("recent_news"):
            score += 15
        
        # Tech stack match
        if any(tech in enrichment.get("technologies", []) 
               for tech in ["AWS", "Azure", "Python", "Microservices"]):
            score += 20
        
        return min(score, 100.0)
    
    async def close(self):
        """Cleanup"""
        await self.session.aclose()
        await self.trinity.close()
