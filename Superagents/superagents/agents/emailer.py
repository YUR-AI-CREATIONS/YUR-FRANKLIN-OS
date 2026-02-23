"""
Email Sequencer Agent
Sends 5-email follow-up sequences with AI-personalized content
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import httpx
from core.trinity_client import TrinityClient
from core.config import SuperagentConfig

# SendGrid email import
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailSequencer:
    """Autonomous email campaign agent"""
    
    # Email sequence templates (will be personalized by AI)
    SEQUENCE = [
        {
            "day": 0,
            "subject": "Can we cut your approval time by 80%?",
            "template": "email_prospecting_1",
        },
        {
            "day": 2,
            "subject": "Saw you just {funding_action}... timing might be right",
            "template": "email_prospecting_2",
        },
        {
            "day": 4,
            "subject": "2-min demo of Trinity (autonomous decision-making)",
            "template": "email_prospecting_3_with_demo",
        },
        {
            "day": 6,
            "subject": "ROI calculator: your approval savings",
            "template": "email_prospecting_4_with_calc",
        },
        {
            "day": 8,
            "subject": "Last chance: Trinity pilot for {company}",
            "template": "email_prospecting_5_scarcity",
        },
    ]
    
    def __init__(self):
        self.trinity = TrinityClient()
        self.session = httpx.AsyncClient()
    
    async def send_email_sequence(self, lead_id: str) -> Dict[str, Any]:
        """Start 5-email sequence for a lead"""
        
        if not lead_id:
            return {"error": "No lead_id provided"}
        
        # Get lead details
        lead = await self.trinity.get_lead(lead_id)
        
        if "error" in lead:
            return {"error": f"Could not fetch lead {lead_id}"}
        
        # Create email campaign in Trinity
        campaign = await self.trinity.create_opportunity(
            lead_id=lead_id,
            title=f"Email Sequence - {lead.get('name', 'Unknown')}",
            value=50000,  # Estimated Trinity contract value
            stage="discovery",
            metadata={
                "campaign_type": "email_sequence",
                "sequence_length": len(self.SEQUENCE),
                "started_at": datetime.now().isoformat(),
            }
        )
        
        results = {
            "lead_id": lead_id,
            "emails_sent": 0,
            "emails_scheduled": 0,
            "campaign_id": campaign.get("id"),
        }
        
        # Schedule each email
        for email_config in self.SEQUENCE:
            try:
                scheduled = await self._schedule_email(
                    lead=lead,
                    email_config=email_config,
                    campaign_id=campaign.get("id"),
                )
                results["emails_scheduled"] += 1
                
            except Exception as e:
                print(f"Error scheduling email: {e}")
        
        return results
    
    async def _schedule_email(self,
                             lead: Dict[str, Any],
                             email_config: Dict[str, Any],
                             campaign_id: str) -> Dict[str, Any]:
        """Schedule and send individual email"""
        
        send_time = datetime.now() + timedelta(days=email_config["day"])
        
        # Personalize content
        subject = await self._personalize_subject(
            email_config["subject"],
            lead
        )
        
        body = await self._generate_email_body(
            email_config["template"],
            lead
        )
        
        # Send via email provider
        result = await self._send_email(
            to_email=lead.get("email", ""),
            to_name=lead.get("name", ""),
            subject=subject,
            body=body,
            metadata={
                "lead_id": lead.get("id"),
                "campaign_id": campaign_id,
                "sequence_day": email_config["day"],
                "template": email_config["template"],
            }
        )
        
        # Log in Trinity
        await self.trinity.log_interaction(
            lead_id=lead.get("id", "unknown"),
            interaction_type="email_sent",
            content=f"Email: {subject}",
            metadata={
                "day": email_config["day"],
                "template": email_config["template"],
                "email_id": result.get("id"),
            }
        )
        
        return result
    
    async def process_email_replies(self) -> Dict[str, Any]:
        """Check for email replies and update lead status"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "replies_processed": 0,
            "leads_advanced": 0,
            "meetings_scheduled": 0,
        }
        
        # TODO: Integrate with email provider to check new emails
        # For Gmail: use Gmail API + IMap
        # For Sendgrid: use event webhook data
        
        return results
    
    async def track_email_engagement(self, lead_id: str) -> Dict[str, Any]:
        """Get email engagement metrics for lead"""
        
        engagement = {
            "lead_id": lead_id,
            "emails_sent": 0,
            "emails_opened": 0,
            "open_rate": 0.0,
            "links_clicked": 0,
            "click_rate": 0.0,
        }
        
        return engagement
    
    # Helper methods
    
    async def _personalize_subject(self, template: str, lead: Dict[str, Any]) -> str:
        """AI-personalize email subject line"""
        
        replacements = {
            "{company}": lead.get("company", "Your company"),
            "{first_name}": lead.get("name", "").split()[0] if lead.get("name") else "",
            "{funding_action}": "raised funding" if lead.get("metadata", {}).get("funding_info") else "is scaling",
        }
        
        subject = template
        for key, value in replacements.items():
            subject = subject.replace(key, value)
        
        return subject
    
    async def _generate_email_body(self, template: str, lead: Dict[str, Any]) -> str:
        """Generate personalized email body"""
        
        lead_name = lead.get('name', 'there')
        lead_company = lead.get('company', 'your company')
        
        # Template 1: Prospecting (initial pain point)
        if template == "email_prospecting_1":
            return f"""Hi {lead_name},

Quick question: how many decisions does your {lead_company} team make each day?

Most companies at your stage (growing fast, scaling approvals) hit bottlenecks when decisions require multiple approvals.

We built Trinity Spine to auto-execute decisions with governance - so approvals happen in seconds, not days.

Worth a 2-min conversation? I can show you how it works.

Best,
{SuperagentConfig.YOUR_NAME}
{SuperagentConfig.YOUR_TITLE}, {SuperagentConfig.COMPANY_NAME}"""
        
        # Template 2: Funding-aware follow-up
        elif template == "email_prospecting_2":
            funding_info = lead.get("metadata", {}).get("funding_info", {})
            announcement = funding_info.get('announcement', 'the funding') if funding_info else 'your growth'
            return f"""Hi {lead_name},

Congrats on {announcement}!

When companies scale, approval bottlenecks usually become evident in the first 90 days. Usually costs teams 5-10% of new revenue.

Trinity Spine solves this by auto-executing decisions within governance bounds.

Relevant for {lead_company}?

{SuperagentConfig.YOUR_NAME}"""
        
        # Template 3: Demo video
        elif template == "email_prospecting_3_with_demo":
            return f"""Hi {lead_name},

Here's that 2-min demo: {SuperagentConfig.PRODUCT_DEMO_URL}

Shows how Trinity handles:
- Finance approvals (gets to $1M in minutes, not weeks)
- Ops decisions (auto-executes based on rules)
- Risk management (PQC crypto + audit trail)

After you watch, let's sync for 15 mins so I can show your use case.

{SuperagentConfig.YOUR_NAME}"""
        
        # Template 4: ROI calculator
        elif template == "email_prospecting_4_with_calc":
            return f"""Hi {lead_name},

Opened the demo but didn't reply yet - totally get it (busy schedule).

Here's a quick ROI calc for {lead_company}:

If you do 200 approvals/day x 2 hours each = 400 hrs/week saved
At $50/hr = $20K/week = $1M/year in recovered time

Trinity costs $50K/year = 20x payback in year 1.

Difference between slow scaling and fast scaling.

Ready to talk?

{SuperagentConfig.YOUR_NAME}"""
        
        # Template 5: Scarcity + alternative
        elif template == "email_prospecting_5_scarcity":
            return f"""Hi {lead_name},

Last message - I promise.

If Trinity isn't right for {lead_company}, I'd love to recommend someone who is.

But if approval bottlenecks are even slightly on your radar, this is worth 15 mins.

Available:
- Tue 2pm ET
- Wed 10am ET  
- Thu 3pm ET

Which works?

{SuperagentConfig.YOUR_NAME}"""
        
        return f"Hi {lead_name}, following up about Trinity Spine for {lead_company}."
    
    async def _send_email(self,
                         to_email: str,
                         to_name: str,
                         subject: str,
                         body: str,
                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via configured provider"""
        
        provider = SuperagentConfig.EMAIL_PROVIDER
        
        if provider == "gmail":
            return await self._send_via_gmail(to_email, to_name, subject, body)
        elif provider == "sendgrid":
            return await self._send_via_sendgrid(to_email, to_name, subject, body)
        else:
            print(f"Unknown email provider: {provider}, defaulting to sendgrid")
            return await self._send_via_sendgrid(to_email, to_name, subject, body)
    
    async def _send_via_gmail(self, to_email: str, to_name: str, subject: str, body: str) -> Dict[str, Any]:
        """Send via Gmail API"""
        # TODO: Implement Gmail API send
        print(f"[Gmail] Would send to {to_email}: {subject}")
        return {"id": f"email_{datetime.now().timestamp()}", "status": "simulated"}
    
    async def _send_via_sendgrid(self, to_email: str, to_name: str, subject: str, body: str) -> Dict[str, Any]:
        """Send via SendGrid API"""
        recipient_email = SuperagentConfig.RECIPIENT_EMAIL or to_email
        
        if not SuperagentConfig.SENDGRID_API_KEY:
            print("❌ SENDGRID_API_KEY not configured")
            return {"status": "error", "error": "SENDGRID_API_KEY not set"}
        
        try:
            sg = SendGridAPIClient(SuperagentConfig.SENDGRID_API_KEY)
            
            # Build HTML body
            html_body = f"<html><body>{body.replace(chr(10), '<br>')}</body></html>"
            
            mail = Mail(
                from_email=(SuperagentConfig.FROM_EMAIL, SuperagentConfig.FROM_NAME),
                to_emails=recipient_email,
                subject=subject,
                plain_text_content=body,
                html_content=html_body
            )
            
            response = sg.send(mail)
            
            print(f"✉️  Email sent to {recipient_email}: {subject} (Status: {response.status_code})")
            
            return {
                "id": f"email_{datetime.utcnow().timestamp()}",
                "to": recipient_email,
                "subject": subject,
                "status": "sent" if response.status_code in [200, 202] else "failed",
                "status_code": response.status_code,
                "sent_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"❌ Error sending email via SendGrid: {e}")
            return {
                "id": f"email_{datetime.utcnow().timestamp()}",
                "to": recipient_email,
                "status": "error",
                "error": str(e),
            }
    
    async def close(self):
        """Cleanup"""
        await self.session.aclose()
        await self.trinity.close()