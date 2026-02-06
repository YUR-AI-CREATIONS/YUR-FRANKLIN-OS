"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      GOVERNANCE & COMPLIANCE ENGINE                          ║
║                                                                              ║
║  Manages approval workflows, licensing, compliance verification,             ║
║  and regulatory adherence throughout the Genesis Pipeline.                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    ESCALATED = "escalated"


class ComplianceCategory(Enum):
    DATA_PRIVACY = "data_privacy"       # GDPR, CCPA
    HEALTHCARE = "healthcare"           # HIPAA, HITECH
    FINANCIAL = "financial"             # SOX, PCI-DSS
    SECURITY = "security"               # SOC2, ISO27001
    ACCESSIBILITY = "accessibility"     # WCAG, ADA
    INDUSTRY = "industry"               # Domain-specific


class LicenseType(Enum):
    PROPRIETARY = "proprietary"
    OPEN_SOURCE = "open_source"
    SAAS = "saas"
    ENTERPRISE = "enterprise"
    FREEMIUM = "freemium"
    CUSTOM = "custom"


@dataclass
class ApprovalGate:
    """Approval checkpoint in the governance workflow"""
    id: str
    name: str
    stage: str
    required_approvers: List[str]
    actual_approvers: List[str] = field(default_factory=list)
    status: ApprovalStatus = ApprovalStatus.PENDING
    conditions: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None


@dataclass
class ComplianceCheck:
    """Compliance verification record"""
    id: str
    category: ComplianceCategory
    requirement: str
    status: str  # passed, failed, not_applicable, pending
    evidence: List[str] = field(default_factory=list)
    remediation: Optional[str] = None
    verified_at: Optional[str] = None


@dataclass
class LicenseAgreement:
    """Software licensing configuration"""
    id: str
    license_type: LicenseType
    terms: Dict[str, Any]
    restrictions: List[str]
    permissions: List[str]
    attribution_required: bool
    commercial_use: bool
    modification_allowed: bool
    distribution_allowed: bool
    warranty_disclaimer: str
    liability_limitation: str
    governing_law: str
    effective_date: str
    expiration_date: Optional[str] = None


class GovernanceEngine:
    """
    Comprehensive Governance Management System
    
    Handles approvals, compliance, licensing, and audit trails.
    """
    
    def __init__(self):
        self.approval_gates: List[ApprovalGate] = []
        self.compliance_checks: List[ComplianceCheck] = []
        self.license: Optional[LicenseAgreement] = None
        self.audit_log: List[Dict[str, Any]] = []
        
    def create_approval_workflow(self, stages: List[str]) -> List[ApprovalGate]:
        """Initialize approval gates for each stage"""
        self.approval_gates = []
        
        gate_configs = {
            "specification": {
                "name": "Requirements Sign-off",
                "approvers": ["product_owner", "tech_lead"]
            },
            "architecture": {
                "name": "Architecture Review Board",
                "approvers": ["architect", "security_officer"]
            },
            "construction": {
                "name": "Code Review Gate",
                "approvers": ["tech_lead", "qa_lead"]
            },
            "validation": {
                "name": "Quality Assurance Gate",
                "approvers": ["qa_lead", "product_owner"]
            },
            "deployment": {
                "name": "Release Approval",
                "approvers": ["release_manager", "ops_lead"]
            },
            "governance": {
                "name": "Legal & Compliance Final",
                "approvers": ["legal_counsel", "compliance_officer"]
            }
        }
        
        for stage in stages:
            config = gate_configs.get(stage, {
                "name": f"{stage.title()} Approval",
                "approvers": ["admin"]
            })
            
            gate = ApprovalGate(
                id=str(uuid.uuid4()),
                name=config["name"],
                stage=stage,
                required_approvers=config["approvers"]
            )
            self.approval_gates.append(gate)
            self._log_action("gate_created", {"gate_id": gate.id, "stage": stage})
            
        return self.approval_gates
    
    def submit_approval(self, gate_id: str, approver: str, 
                       status: ApprovalStatus, notes: str = "",
                       conditions: List[str] = None) -> Dict[str, Any]:
        """Submit approval decision for a gate"""
        gate = self._find_gate(gate_id)
        if not gate:
            return {"error": f"Gate {gate_id} not found"}
        
        if approver not in gate.required_approvers:
            return {"error": f"Approver {approver} not authorized for this gate"}
        
        if approver in gate.actual_approvers:
            return {"error": f"Approver {approver} has already submitted"}
        
        gate.actual_approvers.append(approver)
        gate.notes = notes
        
        if conditions:
            gate.conditions.extend(conditions)
            gate.status = ApprovalStatus.CONDITIONAL
        elif status == ApprovalStatus.REJECTED:
            gate.status = ApprovalStatus.REJECTED
        elif len(gate.actual_approvers) == len(gate.required_approvers):
            gate.status = ApprovalStatus.APPROVED
            gate.resolved_at = datetime.now(timezone.utc).isoformat()
        
        self._log_action("approval_submitted", {
            "gate_id": gate_id,
            "approver": approver,
            "status": status.value
        })
        
        return {
            "gate_id": gate_id,
            "current_status": gate.status.value,
            "approvers_remaining": [
                a for a in gate.required_approvers 
                if a not in gate.actual_approvers
            ],
            "conditions": gate.conditions
        }
    
    def run_compliance_audit(self, artifact: Dict[str, Any], 
                            categories: List[ComplianceCategory] = None) -> Dict[str, Any]:
        """Execute compliance verification across categories"""
        if categories is None:
            categories = list(ComplianceCategory)
            
        self.compliance_checks = []
        results = []
        
        for category in categories:
            checks = self._get_category_requirements(category)
            
            for req in checks:
                check = ComplianceCheck(
                    id=str(uuid.uuid4()),
                    category=category,
                    requirement=req["requirement"],
                    status=self._evaluate_requirement(artifact, req),
                    evidence=req.get("evidence_fields", []),
                    remediation=req.get("remediation") if self._evaluate_requirement(artifact, req) == "failed" else None
                )
                
                if check.status in ["passed", "not_applicable"]:
                    check.verified_at = datetime.now(timezone.utc).isoformat()
                    
                self.compliance_checks.append(check)
                results.append({
                    "category": category.value,
                    "requirement": req["requirement"],
                    "status": check.status,
                    "remediation": check.remediation
                })
        
        passed = sum(1 for c in self.compliance_checks if c.status == "passed")
        failed = sum(1 for c in self.compliance_checks if c.status == "failed")
        total = len(self.compliance_checks)
        
        compliance_score = (passed / total * 100) if total > 0 else 0
        
        self._log_action("compliance_audit", {
            "passed": passed,
            "failed": failed,
            "score": compliance_score
        })
        
        return {
            "compliance_score": round(compliance_score, 2),
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "results": results,
            "audit_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _get_category_requirements(self, category: ComplianceCategory) -> List[Dict]:
        """Get compliance requirements for category"""
        requirements = {
            ComplianceCategory.DATA_PRIVACY: [
                {"requirement": "Data encryption at rest", "check_field": "security.encryption.at_rest", "remediation": "Implement AES-256 encryption for stored data"},
                {"requirement": "Data encryption in transit", "check_field": "security.encryption.in_transit", "remediation": "Enforce TLS 1.3 for all communications"},
                {"requirement": "User consent management", "check_field": "features.consent_management", "remediation": "Add consent tracking and management module"},
                {"requirement": "Data retention policy", "check_field": "policies.data_retention", "remediation": "Define and implement data retention rules"},
                {"requirement": "Right to deletion", "check_field": "features.data_deletion", "remediation": "Implement user data deletion workflow"}
            ],
            ComplianceCategory.SECURITY: [
                {"requirement": "Authentication mechanism", "check_field": "security.authentication", "remediation": "Implement secure authentication (OAuth2, MFA)"},
                {"requirement": "Authorization controls", "check_field": "security.authorization", "remediation": "Implement RBAC or ABAC"},
                {"requirement": "Audit logging", "check_field": "features.audit_log", "remediation": "Add comprehensive audit logging"},
                {"requirement": "Input validation", "check_field": "security.input_validation", "remediation": "Implement input sanitization and validation"},
                {"requirement": "Vulnerability management", "check_field": "security.vulnerability_scanning", "remediation": "Set up automated security scanning"}
            ],
            ComplianceCategory.ACCESSIBILITY: [
                {"requirement": "Keyboard navigation", "check_field": "accessibility.keyboard_nav", "remediation": "Ensure all features accessible via keyboard"},
                {"requirement": "Screen reader support", "check_field": "accessibility.aria_labels", "remediation": "Add ARIA labels to all interactive elements"},
                {"requirement": "Color contrast", "check_field": "accessibility.color_contrast", "remediation": "Ensure WCAG AA color contrast ratios"},
                {"requirement": "Alt text for images", "check_field": "accessibility.alt_text", "remediation": "Add descriptive alt text to all images"}
            ],
            ComplianceCategory.HEALTHCARE: [
                {"requirement": "PHI encryption", "check_field": "hipaa.phi_encryption", "remediation": "Encrypt all Protected Health Information"},
                {"requirement": "Access controls", "check_field": "hipaa.access_controls", "remediation": "Implement minimum necessary access principle"},
                {"requirement": "Audit trails", "check_field": "hipaa.audit_trails", "remediation": "Log all PHI access and modifications"},
                {"requirement": "BAA compliance", "check_field": "hipaa.baa_ready", "remediation": "Ensure Business Associate Agreement readiness"}
            ],
            ComplianceCategory.FINANCIAL: [
                {"requirement": "PCI data handling", "check_field": "pci.card_data_handling", "remediation": "Never store CVV, encrypt card data"},
                {"requirement": "Transaction logging", "check_field": "pci.transaction_logs", "remediation": "Implement immutable transaction audit trail"},
                {"requirement": "Fraud detection", "check_field": "features.fraud_detection", "remediation": "Add fraud detection mechanisms"}
            ],
            ComplianceCategory.INDUSTRY: [
                {"requirement": "Industry standards adherence", "check_field": "compliance.industry_standards", "remediation": "Review and implement applicable industry standards"}
            ]
        }
        return requirements.get(category, [])
    
    def _evaluate_requirement(self, artifact: Dict, requirement: Dict) -> str:
        """Evaluate if artifact meets requirement"""
        check_field = requirement.get("check_field", "")
        
        # Navigate nested fields
        parts = check_field.split(".")
        value = artifact
        
        try:
            for part in parts:
                value = value.get(part, {})
            
            if value and value != {}:
                return "passed"
            else:
                return "failed"
        except (AttributeError, TypeError):
            return "failed"
    
    def configure_license(self, license_type: LicenseType, 
                         custom_terms: Dict[str, Any] = None) -> LicenseAgreement:
        """Configure software licensing"""
        base_configs = {
            LicenseType.PROPRIETARY: {
                "restrictions": ["No redistribution", "No modification", "No reverse engineering"],
                "permissions": ["Use for intended purpose", "Create backups"],
                "attribution_required": False,
                "commercial_use": True,
                "modification_allowed": False,
                "distribution_allowed": False
            },
            LicenseType.OPEN_SOURCE: {
                "restrictions": ["Must include license", "Must include copyright"],
                "permissions": ["Commercial use", "Modification", "Distribution", "Private use"],
                "attribution_required": True,
                "commercial_use": True,
                "modification_allowed": True,
                "distribution_allowed": True
            },
            LicenseType.SAAS: {
                "restrictions": ["No redistribution", "Usage limits apply", "Subscription required"],
                "permissions": ["Access via internet", "API access", "Data export"],
                "attribution_required": False,
                "commercial_use": True,
                "modification_allowed": False,
                "distribution_allowed": False
            },
            LicenseType.ENTERPRISE: {
                "restrictions": ["Named users only", "Single organization"],
                "permissions": ["Unlimited internal use", "Priority support", "Custom integrations"],
                "attribution_required": False,
                "commercial_use": True,
                "modification_allowed": True,
                "distribution_allowed": False
            },
            LicenseType.FREEMIUM: {
                "restrictions": ["Feature limitations", "Usage caps", "Upgrade required for full access"],
                "permissions": ["Basic features free", "Personal use"],
                "attribution_required": False,
                "commercial_use": False,
                "modification_allowed": False,
                "distribution_allowed": False
            }
        }
        
        config = base_configs.get(license_type, base_configs[LicenseType.PROPRIETARY])
        
        if custom_terms:
            config.update(custom_terms)
        
        self.license = LicenseAgreement(
            id=str(uuid.uuid4()),
            license_type=license_type,
            terms=config,
            restrictions=config["restrictions"],
            permissions=config["permissions"],
            attribution_required=config["attribution_required"],
            commercial_use=config["commercial_use"],
            modification_allowed=config["modification_allowed"],
            distribution_allowed=config["distribution_allowed"],
            warranty_disclaimer="THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND.",
            liability_limitation="IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY.",
            governing_law=custom_terms.get("governing_law", "State of Delaware, USA") if custom_terms else "State of Delaware, USA",
            effective_date=datetime.now(timezone.utc).isoformat()
        )
        
        self._log_action("license_configured", {
            "license_type": license_type.value,
            "license_id": self.license.id
        })
        
        return self.license
    
    def generate_license_document(self) -> str:
        """Generate human-readable license document"""
        if not self.license:
            return "No license configured"
        
        doc = f"""
================================================================================
                            SOFTWARE LICENSE AGREEMENT
================================================================================

License Type: {self.license.license_type.value.upper()}
License ID: {self.license.id}
Effective Date: {self.license.effective_date}

--------------------------------------------------------------------------------
                                 PERMISSIONS
--------------------------------------------------------------------------------
{chr(10).join(f'  ✓ {p}' for p in self.license.permissions)}

--------------------------------------------------------------------------------
                                 RESTRICTIONS
--------------------------------------------------------------------------------
{chr(10).join(f'  ✗ {r}' for r in self.license.restrictions)}

--------------------------------------------------------------------------------
                               LICENSE TERMS
--------------------------------------------------------------------------------
Commercial Use: {'Permitted' if self.license.commercial_use else 'Not Permitted'}
Modification: {'Permitted' if self.license.modification_allowed else 'Not Permitted'}
Distribution: {'Permitted' if self.license.distribution_allowed else 'Not Permitted'}
Attribution Required: {'Yes' if self.license.attribution_required else 'No'}

--------------------------------------------------------------------------------
                                  DISCLAIMER
--------------------------------------------------------------------------------
{self.license.warranty_disclaimer}

--------------------------------------------------------------------------------
                           LIMITATION OF LIABILITY
--------------------------------------------------------------------------------
{self.license.liability_limitation}

--------------------------------------------------------------------------------
                               GOVERNING LAW
--------------------------------------------------------------------------------
This agreement shall be governed by the laws of {self.license.governing_law}.

================================================================================
"""
        return doc
    
    def _find_gate(self, gate_id: str) -> Optional[ApprovalGate]:
        """Find approval gate by ID"""
        for gate in self.approval_gates:
            if gate.id == gate_id:
                return gate
        return None
    
    def _log_action(self, action: str, details: Dict[str, Any]):
        """Record action in audit log"""
        self.audit_log.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_governance_status(self) -> Dict[str, Any]:
        """Get comprehensive governance status"""
        approved_gates = sum(1 for g in self.approval_gates if g.status == ApprovalStatus.APPROVED)
        pending_gates = sum(1 for g in self.approval_gates if g.status == ApprovalStatus.PENDING)
        
        passed_compliance = sum(1 for c in self.compliance_checks if c.status == "passed")
        total_compliance = len(self.compliance_checks)
        
        return {
            "approval_gates": {
                "total": len(self.approval_gates),
                "approved": approved_gates,
                "pending": pending_gates,
                "gates": [
                    {
                        "id": g.id,
                        "name": g.name,
                        "stage": g.stage,
                        "status": g.status.value,
                        "conditions": g.conditions
                    } for g in self.approval_gates
                ]
            },
            "compliance": {
                "score": round((passed_compliance / total_compliance * 100), 2) if total_compliance > 0 else 0,
                "passed": passed_compliance,
                "total": total_compliance
            },
            "license": {
                "configured": self.license is not None,
                "type": self.license.license_type.value if self.license else None,
                "id": self.license.id if self.license else None
            },
            "audit_entries": len(self.audit_log)
        }
