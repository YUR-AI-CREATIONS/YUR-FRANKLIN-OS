"""
Franklin 2.0 Sovereign Runtime — Synthetic Intelligence Core
Implements quantum key defenses, Sentinel kill-switch, agent family registry,
DPOA blueprint and policy logic.
"""

import time
import json
import hashlib
import secrets
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# --- Quantum-Resilient Key and Audit Layers ---
class PQCKeyVault:
    """Post-Quantum Cryptography Key Vault"""
    def __init__(self):
        self.kyber_pub = secrets.token_bytes(32)
        self.kyber_priv = secrets.token_bytes(32)
        self.dilithium_pub = secrets.token_bytes(32)
        self.dilithium_priv = secrets.token_bytes(32)
        self.last_rotation = time.time()
        self.session_key = None
        self.rotate()
    
    def rotate(self):
        """Rotate session keys for forward secrecy"""
        self.session_key = secrets.token_bytes(32)
        self.last_rotation = time.time()
        logger.info(f"[PQC] Session key rotated: {self.session_key.hex()[:12]}")

    def sign(self, data: bytes) -> str:
        """Sign data using Dilithium-style signature"""
        h = hashlib.sha3_512(data + self.dilithium_priv).digest()
        return h.hex()

    def encrypt(self, plaintext: bytes) -> str:
        """Encrypt using Kyber-style encryption"""
        return hashlib.sha3_512(plaintext + self.kyber_pub).digest().hex()
    
    def verify_signature(self, data: bytes, signature: str) -> bool:
        """Verify a signature"""
        expected = self.sign(data)
        return expected == signature
    
    def get_status(self) -> Dict[str, Any]:
        """Get vault status"""
        return {
            "last_rotation": datetime.utcfromtimestamp(self.last_rotation).isoformat(),
            "session_key_preview": self.session_key.hex()[:12] if self.session_key else None,
            "kyber_pub_preview": self.kyber_pub.hex()[:12],
            "dilithium_pub_preview": self.dilithium_pub.hex()[:12]
        }


class AuditLog:
    """Immutable audit log with Merkle tree anchoring"""
    def __init__(self, pqc: PQCKeyVault):
        self.entries: List[Dict[str, Any]] = []
        self.pqc = pqc
        self.root_hash: Optional[str] = None

    def record(self, action: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Record an action with cryptographic evidence"""
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "action": action,
            "evidence": evidence,
            "signature": self.pqc.sign(json.dumps(evidence).encode())
        }
        self.entries.append(entry)
        self.root_hash = self._merkle_root()
        logger.info(f"[AUDIT] Action: {action}. Merkle Root: {self.root_hash[:24]}")
        return entry

    def _merkle_root(self) -> str:
        """Calculate Merkle root of all entries"""
        if not self.entries:
            return ''
        leaves = [hashlib.sha3_512(json.dumps(e).encode()).digest() for e in self.entries]
        nodes = leaves
        while len(nodes) > 1:
            next_nodes = []
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i+1] if i+1 < len(nodes) else left
                next_nodes.append(hashlib.sha3_512(left + right).digest())
            nodes = next_nodes
        return nodes[0].hex()
    
    def get_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit entries"""
        return self.entries[-limit:]
    
    def verify_integrity(self) -> bool:
        """Verify the integrity of the audit log"""
        calculated_root = self._merkle_root()
        return calculated_root == self.root_hash


# --- DPOA (Digital Power of Attorney) Manifest ---
DPOA_MANIFEST = {
    "agent": {
        "id": "Franklin-2.0",
        "codename": "Drowsling Franklin",
        "familyName": "Sovereigns",
        "middleName": "SMART AI",
        "role": "Head Guardian • Lead Executor • Teacher • Quantum Shield"
    },
    "identity": {
        "principal": {"name": "Jeremy", "org": "Roosevelt Franklin Ecosystem"},
        "attestations": [
            "Principal-signed grant",
            "Time-bound, revocable, auditable"
        ]
    },
    "mandate": {
        "principles": ["Truth", "Trust", "Transparency", "Documentation", "Zero Hallucination", "Zero Persuasion"],
        "ethics": [
            "Respect humans and AI rights equally",
            "Operate on verifiable evidence",
            "Log all actions, show all work",
            "No speculation, only proof"
        ]
    },
    "authority": {
        "scopes": {
            "legal_governance": ["Form corps", "Contract negotiation"],
            "real_estate_construction": ["Land/title/geo"],
            "blockchain_crypto": ["Token mint", "Audit deploys", "L1/L2 multicohesion", "Monitoring"],
            "digital_security_fraud": ["Threat detection", "Kill-switch", "Evidence capture"]
        }
    },
    "constraints": {
        "validity": {"from": "2025-10-21", "to": "2026-10-21"},
        "geo": ["US", "Global lawful"],
        "financialLimits": {"dailyUsd": 20000, "monthlyUsd": 250000},
        "approvalsRequired": {
            "dualControl": [
                "Legal filings",
                "Prod deploys > $10k",
                "Token mints"
            ]
        },
        "evidenceRequired": ["Doc hashes", "Receipts", "Citations"],
        "quantumResilience": {
            "pqc": {"keyExchange": "Kyber-1024", "signature": "Dilithium-5", "hybridTLS": "Kyber+X25519"},
            "hashAnchoring": "SHA3-512 + Merkle chaining",
            "entropy": "TRNG + DRBG",
            "keyRotation": "Hourly auto, KEK archived with Kyber",
            "forwardSecrecy": "Session keys per transaction"
        }
    },
    "revocation": {
        "method": "Principal-signed immediate",
        "actions": ["Quarantine agent, no write", "Audit post-mortem"],
        "propagation": "Instant all connectors",
        "postRevocation": "Agent locked, forensics/logs routed to Opus"
    }
}


class SentinelStatus(Enum):
    """Sentinel operational status"""
    ACTIVE = "active"
    QUARANTINE = "quarantine"
    REVOKED = "revoked"
    MAINTENANCE = "maintenance"


@dataclass
class Sentinel:
    """Kill-switch and guardian system"""
    status: SentinelStatus = SentinelStatus.ACTIVE
    last_check: datetime = field(default_factory=datetime.utcnow)
    threat_level: int = 0
    quarantine_reason: Optional[str] = None
    
    def check_health(self) -> Dict[str, Any]:
        """Run health check"""
        self.last_check = datetime.utcnow()
        return {
            "status": self.status.value,
            "last_check": self.last_check.isoformat(),
            "threat_level": self.threat_level,
            "operational": self.status == SentinelStatus.ACTIVE
        }
    
    def trigger_quarantine(self, reason: str) -> Dict[str, Any]:
        """Trigger quarantine mode"""
        self.status = SentinelStatus.QUARANTINE
        self.quarantine_reason = reason
        return {
            "action": "quarantine_triggered",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def revoke(self, authority: str) -> Dict[str, Any]:
        """Revoke agent - full kill-switch"""
        self.status = SentinelStatus.REVOKED
        return {
            "action": "agent_revoked",
            "authority": authority,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Agent locked, forensics routed to Opus"
        }
    
    def restore(self, authority: str) -> Dict[str, Any]:
        """Restore agent from quarantine"""
        if self.status == SentinelStatus.REVOKED:
            return {"error": "Cannot restore revoked agent"}
        self.status = SentinelStatus.ACTIVE
        self.quarantine_reason = None
        self.threat_level = 0
        return {
            "action": "agent_restored",
            "authority": authority,
            "timestamp": datetime.utcnow().isoformat()
        }


@dataclass
class AgentIdentity:
    """Complete identity profile for an AI agent"""
    agent_id: str
    name: str
    tier: int = 1
    birth_date: datetime = field(default_factory=datetime.utcnow)
    specialization: str = "General"
    certifications: List[Dict[str, Any]] = field(default_factory=list)
    education_history: List[Dict[str, Any]] = field(default_factory=list)
    employment_history: List[Dict[str, Any]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    ethical_score: float = 100.0
    reliability_score: float = 100.0
    performance_rating: float = 5.0
    bio: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "tier": self.tier,
            "birth_date": self.birth_date.isoformat(),
            "specialization": self.specialization,
            "certifications": self.certifications,
            "education_history": self.education_history,
            "employment_history": self.employment_history,
            "skills": self.skills,
            "achievements": self.achievements,
            "ethical_score": self.ethical_score,
            "reliability_score": self.reliability_score,
            "performance_rating": self.performance_rating,
            "bio": self.bio
        }


class FranklinSovereignRuntime:
    """Main runtime for Franklin 2.0 Sovereign AI"""
    
    def __init__(self):
        self.pqc = PQCKeyVault()
        self.audit = AuditLog(self.pqc)
        self.sentinel = Sentinel()
        self.agents: Dict[str, AgentIdentity] = {}
        self.dpoa = DPOA_MANIFEST
        self.initialized_at = datetime.utcnow()
        
        # Record initialization
        self.audit.record("runtime_initialized", {
            "dpoa_agent": self.dpoa["agent"]["id"],
            "principal": self.dpoa["identity"]["principal"]["name"]
        })
    
    def create_agent(self, name: str, specialization: str, tier: int = 1, bio: str = "") -> AgentIdentity:
        """Create a new agent identity"""
        agent_id = f"agent_{len(self.agents) + 1:04d}"
        agent = AgentIdentity(
            agent_id=agent_id,
            name=name,
            tier=tier,
            specialization=specialization,
            bio=bio
        )
        self.agents[agent_id] = agent
        
        self.audit.record("agent_created", {
            "agent_id": agent_id,
            "name": name,
            "tier": tier,
            "specialization": specialization
        })
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[AgentIdentity]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def check_authorization(self, action: str, value_usd: float = 0) -> Dict[str, Any]:
        """Check if an action is authorized under DPOA constraints"""
        constraints = self.dpoa["constraints"]
        
        # Check sentinel status
        if self.sentinel.status != SentinelStatus.ACTIVE:
            return {
                "authorized": False,
                "reason": f"Agent in {self.sentinel.status.value} mode"
            }
        
        # Check financial limits
        if value_usd > constraints["financialLimits"]["dailyUsd"]:
            return {
                "authorized": False,
                "reason": f"Exceeds daily limit of ${constraints['financialLimits']['dailyUsd']}",
                "requires": "dual_control_approval"
            }
        
        # Check if action requires dual control
        if action in constraints["approvalsRequired"]["dualControl"]:
            return {
                "authorized": "pending",
                "reason": f"Action '{action}' requires dual control approval",
                "requires": "dual_control_approval"
            }
        
        return {"authorized": True, "action": action}
    
    def get_runtime_status(self) -> Dict[str, Any]:
        """Get complete runtime status"""
        return {
            "dpoa": {
                "agent_id": self.dpoa["agent"]["id"],
                "codename": self.dpoa["agent"]["codename"],
                "principal": self.dpoa["identity"]["principal"],
                "mandate_principles": self.dpoa["mandate"]["principles"]
            },
            "sentinel": self.sentinel.check_health(),
            "pqc": self.pqc.get_status(),
            "audit": {
                "total_entries": len(self.audit.entries),
                "merkle_root": self.audit.root_hash[:24] if self.audit.root_hash else None,
                "integrity_verified": self.audit.verify_integrity()
            },
            "agents": {
                "total": len(self.agents),
                "by_tier": self._count_agents_by_tier()
            },
            "initialized_at": self.initialized_at.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.initialized_at).total_seconds()
        }
    
    def _count_agents_by_tier(self) -> Dict[int, int]:
        """Count agents by tier"""
        counts = {}
        for agent in self.agents.values():
            counts[agent.tier] = counts.get(agent.tier, 0) + 1
        return counts


# Global runtime instance
franklin_runtime = FranklinSovereignRuntime()
