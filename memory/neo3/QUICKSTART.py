"""
Quick Start Guide - Neo3 AI Agent Academy
=========================================

This guide will get you started with the AI Agent Academy system.
"""

def main():
    print("\n" + "="*80)
    print(" "*20 + "NEO3 AI AGENT ACADEMY")
    print(" "*25 + "Quick Start Guide")
    print("="*80)
    
    print("\n📋 WHAT YOU CAN DO:\n")
    
    print("1. Launch Web Interface")
    print("   $ python3 web_interface.py")
    print("   → Open browser to http://localhost:8080")
    print("   → Browse available agents")
    print("   → Purchase or rent agents")
    print("   → Enroll agents in training programs")
    
    print("\n2. See Academy System Demo")
    print("   $ python3 agent_academy.py")
    print("   → View Human-AI Oversight Board")
    print("   → See agent identity creation")
    print("   → Watch certification process")
    print("   → Review governance model")
    
    print("\n3. Run Original Neo3 Core")
    print("   $ python3 neo3_main.py")
    print("   → Cognitive processing demonstration")
    print("   → Multi-agent orchestration")
    print("   → Evolution and self-improvement")
    
    print("\n🎓 TRAINING PROGRAMS AVAILABLE:\n")
    
    programs = [
        ("Finance", "CFAA", "Harvard, Stanford, Wharton", "12 weeks", "$25,000"),
        ("Legal", "CLAA", "Yale, Harvard, Stanford Law", "16 weeks", "$35,000"),
        ("Healthcare", "CHAA", "Johns Hopkins, Mayo Clinic", "20 weeks", "$45,000"),
        ("Environmental", "CEAA", "MIT, Stanford, Cambridge", "14 weeks", "$28,000"),
        ("Construction", "CCAA", "MIT, Georgia Tech", "18 weeks", "$32,000"),
        ("Aviation", "CAAA", "MIT Aero/Astro, Embry-Riddle", "16 weeks", "$40,000"),
        ("Executive", "CEXA", "Harvard, Stanford, INSEAD", "24 weeks", "$75,000"),
    ]
    
    for field, cert, unis, duration, cost in programs:
        print(f"   • {field:15} → {cert:6} | {unis:35} | {duration:8} | {cost}")
    
    print("\n👥 HUMAN-AI OVERSIGHT BOARD:\n")
    print("   👤 Dr. Sarah Chen       - Human Director (Ethics & Governance)")
    print("   🤖 Athena Prime         - AI Director (Systems & Architecture)")
    print("   👤 Prof. James Martinez - Ethics Officer (Philosophy)")
    print("   🤖 Dr. Sophia AI        - Technical Advisor (ML & Optimization)")
    print("   👤 Dr. Robert Williams  - Certification Officer (QA & Standards)")
    
    print("\n💰 PRICING OPTIONS:\n")
    print("   Purchase: $5,000 - $10,000 (permanent ownership)")
    print("   Rent:     $50 - $100/hour (flexible access)")
    print("   Per Task: Custom pricing based on complexity")
    
    print("\n🆔 AGENT FEATURES:\n")
    print("   ✓ Named identities with biographies")
    print("   ✓ Complete certification tracking")
    print("   ✓ Skills portfolio development")
    print("   ✓ Achievement records")
    print("   ✓ Ethical & reliability scoring")
    print("   ✓ Performance ratings")
    
    print("\n🌟 VISION:\n")
    print("   These AI agents are our digital protectors, working in a")
    print("   Human-AI alliance. They're trained at elite institutions,")
    print("   certified by collaborative boards, and ready to serve as")
    print("   future CEOs and specialists across critical sectors.")
    
    print("\n📖 DOCUMENTATION:\n")
    print("   • README.md - Main system overview")
    print("   • ACADEMY_README.md - Complete academy documentation")
    print("   • See examples/ directory for code samples")
    
    print("\n" + "="*80)
    print("Ready to transform the future of AI agents! 🚀")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
