# Neo3 System Testing Guide

## Overview

This guide provides comprehensive testing procedures for all Neo3 features. Follow these tests to verify that the complete system integration is working correctly.

## Pre-Testing Checklist

Before starting tests, ensure all services are running:

- [ ] Python Marketplace Service (Port 8080)
- [ ] Express Backend API (Port 3000)
- [ ] React Frontend (Port 3000 dev server or build)
- [ ] Browser console open (F12) to monitor for errors

## Test Environment Setup

```bash
# Terminal 1: Start Python Marketplace
python3 web_interface.py

# Terminal 2: Start Express Backend
cd backend && npm install && npm start

# Terminal 3: Start React Frontend
cd frontend && npm install && npm start
```

Wait for all services to start successfully before proceeding with tests.

## Feature Testing Checklist

### 1. Dashboard Tests

#### 1.1 Service Status Display
- [ ] Navigate to http://localhost:3000
- [ ] Dashboard loads without errors
- [ ] API Status card displays "running" or "healthy"
- [ ] PyQMC Service card shows status
- [ ] Quasi-Monte Carlo card shows "Ready"
- [ ] Security card shows "Quantum-Safe"
- [ ] All status badges are green (success state)

#### 1.2 Navigation Tests
- [ ] Three navigation tabs visible: Dashboard, Marketplace, Academy
- [ ] Dashboard tab is active by default
- [ ] Clicking Marketplace tab navigates to /marketplace
- [ ] Clicking Academy tab navigates to /academy
- [ ] Browser back/forward buttons work correctly
- [ ] Active tab is highlighted

#### 1.3 Responsive Design
- [ ] Resize browser to mobile width (< 768px)
- [ ] Navigation stacks vertically on mobile
- [ ] Cards stack in single column on mobile
- [ ] All content remains readable and functional

### 2. Agent Marketplace Tests

#### 2.1 Marketplace Loading
- [ ] Navigate to /marketplace
- [ ] Page title shows "🤖 Agent Marketplace"
- [ ] Subtitle displays correctly
- [ ] Loading spinner appears briefly
- [ ] 7 agent cards load successfully

#### 2.2 Agent Display
Verify all 7 agents are displayed with correct information:

**Analyst Alpha**
- [ ] Name: "Analyst Alpha"
- [ ] Type: analyzer
- [ ] Specialization: finance
- [ ] Rating: 5.0
- [ ] Level: 1.0
- [ ] Purchase price: $5,000
- [ ] Hourly rate: $50

**Legal Eagle**
- [ ] Name: "Legal Eagle"
- [ ] Type: analyzer
- [ ] Specialization: legal
- [ ] Purchase price: $7,500
- [ ] Hourly rate: $75

**Strategy Sigma**
- [ ] Name: "Strategy Sigma"
- [ ] Type: strategist
- [ ] Specialization: finance
- [ ] Purchase price: $10,000
- [ ] Hourly rate: $100

**Builder Beta**
- [ ] Name: "Builder Beta"
- [ ] Type: executor
- [ ] Specialization: construction
- [ ] Purchase price: $6,000
- [ ] Hourly rate: $60

**Efficiency Epsilon**
- [ ] Name: "Efficiency Epsilon"
- [ ] Type: optimizer
- [ ] Specialization: environmental
- [ ] Purchase price: $8,000
- [ ] Hourly rate: $80

**Aviation Ace**
- [ ] Name: "Aviation Ace"
- [ ] Type: strategist
- [ ] Specialization: aviation
- [ ] Purchase price: $9,000
- [ ] Hourly rate: $90

**Health Guardian**
- [ ] Name: "Health Guardian"
- [ ] Type: analyzer
- [ ] Specialization: healthcare
- [ ] Purchase price: $8,500
- [ ] Hourly rate: $85

#### 2.3 Filter and Search Tests
- [ ] Search box is visible and functional
- [ ] Type "legal" in search - only Legal Eagle appears
- [ ] Clear search - all 7 agents reappear
- [ ] Type "finance" - Analyst Alpha and Strategy Sigma appear
- [ ] Select "analyzer" from Type filter - 3 agents appear
- [ ] Select "finance" from Specialization filter - 2 agents appear
- [ ] Combine filters - results update correctly
- [ ] Results count updates correctly ("Showing X of 7 agents")
- [ ] Reset all filters - all agents reappear

#### 2.4 Purchase Flow Test
- [ ] Click "Purchase" button on Analyst Alpha
- [ ] Purchase modal opens
- [ ] Modal shows agent name: "Analyst Alpha"
- [ ] Modal shows purchase price: $5,000
- [ ] Modal shows rating and experience level
- [ ] User ID field is pre-filled with "demo_user"
- [ ] Change user ID to "test_user_123"
- [ ] Click "Confirm Purchase"
- [ ] Success alert appears
- [ ] Alert message includes agent name
- [ ] Modal closes after confirmation
- [ ] Page remains functional after purchase

#### 2.5 Rental Flow Test
- [ ] Click "Rent" button on Legal Eagle
- [ ] Rental modal opens
- [ ] Modal shows agent name: "Legal Eagle"
- [ ] Modal shows hourly rate: $75/hr
- [ ] Hours slider is visible and set to 8 by default
- [ ] Total cost displays: $600 (8 × $75)
- [ ] Move slider to 1 hour - cost updates to $75
- [ ] Move slider to 24 hours - cost updates to $1,800
- [ ] Move slider to 168 hours (1 week) - cost updates correctly
- [ ] User ID field is pre-filled
- [ ] Click "Confirm Rental"
- [ ] Success alert appears with rental ID and total cost
- [ ] Modal closes after confirmation

#### 2.6 Card Hover Effects
- [ ] Hover over any agent card - card elevates
- [ ] Card shadow increases on hover
- [ ] Hover off - card returns to normal state
- [ ] Transitions are smooth

#### 2.7 Error Handling
- [ ] Stop Python marketplace service (Ctrl+C in Terminal 1)
- [ ] Refresh marketplace page
- [ ] Error message appears: "Marketplace service unavailable"
- [ ] Retry button is visible
- [ ] Restart marketplace service
- [ ] Click Retry button
- [ ] Agents reload successfully

### 3. Academy Programs Tests

#### 3.1 Academy Loading
- [ ] Navigate to /academy
- [ ] Page title shows "🎓 AI Agent Academy"
- [ ] Subtitle displays correctly
- [ ] Institution names listed (Harvard, Yale, Stanford, MIT, etc.)
- [ ] Loading spinner appears briefly
- [ ] 6 program cards load successfully

#### 3.2 Program Display
Verify all 6 programs are displayed:

**Elite Finance Program**
- [ ] Name: "Elite Finance Program"
- [ ] Institutions: Harvard, Stanford, Wharton
- [ ] Duration: 12 weeks
- [ ] Certification: "Certified Financial AI Agent"
- [ ] 4 skills badges displayed
- [ ] Skills include: Financial Analysis, Risk Assessment, Portfolio Management, Market Prediction

**Advanced Legal AI Program**
- [ ] Name: "Advanced Legal AI Program"
- [ ] Institutions: Yale, Harvard, Stanford
- [ ] Duration: 16 weeks
- [ ] 4 skills displayed

**Medical Intelligence Program**
- [ ] Name: "Medical Intelligence Program"
- [ ] Institutions: Johns Hopkins, Stanford, Mayo Clinic
- [ ] Duration: 20 weeks
- [ ] Healthcare-related skills displayed

**Environmental Science Program**
- [ ] Name: "Environmental Science Program"
- [ ] Institutions: MIT, Stanford, Cambridge
- [ ] Duration: 14 weeks

**Infrastructure & Construction Program**
- [ ] Name: "Infrastructure & Construction Program"
- [ ] Institutions: MIT, Stanford, Georgia Tech
- [ ] Duration: 18 weeks

**Aviation & Aerospace Program**
- [ ] Name: "Aviation & Aerospace Program"
- [ ] Institutions: MIT, Stanford, Embry-Riddle
- [ ] Duration: 16 weeks

#### 3.3 Program Card Styling
- [ ] Each program has a unique color-coded left border
- [ ] Finance: Green border
- [ ] Legal: Gray border
- [ ] Healthcare: Red border
- [ ] Environmental: Teal border
- [ ] Construction: Orange border
- [ ] Aviation: Blue border

#### 3.4 Enrollment Flow Test
- [ ] Click "Enroll Agent" on Finance Program
- [ ] Enrollment modal opens
- [ ] Modal header matches program color
- [ ] Program name displays correctly
- [ ] Institutions listed
- [ ] Duration shown
- [ ] Certification name displayed
- [ ] Agent ID field pre-filled with "analyst_alpha"
- [ ] Change to "legal_eagle"
- [ ] Click "Confirm Enrollment"
- [ ] Success alert appears with program details
- [ ] Modal closes

#### 3.5 Modal Cancel Test
- [ ] Click "Enroll Agent" on any program
- [ ] Modal opens
- [ ] Click "Cancel" button
- [ ] Modal closes without action
- [ ] Click "Enroll Agent" again
- [ ] Modal opens
- [ ] Click outside modal (on overlay)
- [ ] Modal closes without action

#### 3.6 Program Hover Effects
- [ ] Hover over any program card
- [ ] Card elevates with smooth animation
- [ ] Shadow increases
- [ ] Skills badges may have hover effects

### 4. Cross-Feature Tests

#### 4.1 Navigation Flow Test
- [ ] Start at Dashboard
- [ ] Click Marketplace
- [ ] Purchase an agent
- [ ] Navigate to Academy
- [ ] Enroll the purchased agent
- [ ] Return to Dashboard
- [ ] All navigation works smoothly

#### 4.2 Browser Console Tests
- [ ] Open browser console (F12)
- [ ] Navigate through all pages
- [ ] No JavaScript errors (except allowed external extension warnings)
- [ ] No failed network requests (404, 500 errors)
- [ ] Console logs show API requests being made
- [ ] Responses are successful (200 status)

#### 4.3 Network Tab Inspection
- [ ] Open Network tab in developer tools
- [ ] Navigate to Marketplace
- [ ] Verify request to: /api/marketplace/agents
- [ ] Status: 200 OK
- [ ] Response contains 7 agents
- [ ] Navigate to Academy
- [ ] Verify request to: /api/marketplace/programs
- [ ] Status: 200 OK
- [ ] Response contains 6 programs

### 5. API Endpoint Tests

Run these curl commands to test backend directly:

#### 5.1 Health Check
```bash
curl http://localhost:3000/health
```
- [ ] Returns JSON with status: "healthy"
- [ ] Includes timestamp
- [ ] Includes uptime

#### 5.2 Get Agents
```bash
curl http://localhost:3000/api/marketplace/agents
```
- [ ] Returns JSON with "agents" array
- [ ] Array contains 7 agents
- [ ] Each agent has: id, name, type, specialization, prices

#### 5.3 Get Programs
```bash
curl http://localhost:3000/api/marketplace/programs
```
- [ ] Returns JSON with "programs" object
- [ ] Contains 6 program keys: finance, legal, healthcare, environmental, construction, aviation
- [ ] Each program has: name, institutions, duration, certification, skills

#### 5.4 Purchase Agent
```bash
curl -X POST http://localhost:3000/api/marketplace/purchase \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "analyst_alpha", "user_id": "test_user"}'
```
- [ ] Returns success: true
- [ ] Includes message
- [ ] Includes agent object

#### 5.5 Rent Agent
```bash
curl -X POST http://localhost:3000/api/marketplace/rent \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "legal_eagle", "user_id": "test_user", "hours": 10}'
```
- [ ] Returns success: true
- [ ] Includes rental_id
- [ ] Includes calculated cost (750 for 10 hours at $75/hr)

#### 5.6 Enroll Agent
```bash
curl -X POST http://localhost:3000/api/marketplace/enroll \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "analyst_alpha", "program": "finance"}'
```
- [ ] Returns success: true
- [ ] Includes enrollment details
- [ ] Shows program name and institutions

### 6. Responsive Design Tests

#### 6.1 Desktop (1920x1080)
- [ ] All cards display in grid (multiple columns)
- [ ] Navigation is horizontal
- [ ] No horizontal scrolling
- [ ] All content readable

#### 6.2 Tablet (768x1024)
- [ ] Cards adjust to 2 columns
- [ ] Navigation remains horizontal or stacks
- [ ] Modals centered and readable
- [ ] Touch interactions work

#### 6.3 Mobile (375x667)
- [ ] Cards display in single column
- [ ] Navigation stacks vertically
- [ ] Filters stack vertically
- [ ] Modals fit screen width
- [ ] Text remains readable
- [ ] Buttons are tap-friendly

### 7. Performance Tests

- [ ] Initial page load < 3 seconds
- [ ] Marketplace loads < 2 seconds
- [ ] Academy loads < 2 seconds
- [ ] Smooth scrolling throughout
- [ ] No lag when hovering cards
- [ ] Modal opens/closes smoothly
- [ ] Navigation is instant

### 8. Browser Compatibility

Test in multiple browsers:

#### Chrome
- [ ] All features work
- [ ] No console errors
- [ ] Styling correct

#### Firefox
- [ ] All features work
- [ ] No console errors
- [ ] Styling correct

#### Safari (if available)
- [ ] All features work
- [ ] No console errors
- [ ] Styling correct

#### Edge
- [ ] All features work
- [ ] No console errors
- [ ] Styling correct

## Issue Tracking

Use this section to note any issues found during testing:

| Issue | Severity | Page/Feature | Status |
|-------|----------|--------------|--------|
| Example: Modal not closing | High | Marketplace | Fixed |
|  |  |  |  |

## Test Summary

**Date Tested**: _______________

**Tester**: _______________

**Environment**:
- Python Version: _______________
- Node Version: _______________
- Browser: _______________

**Overall Status**: ⬜ Pass  ⬜ Fail  ⬜ Partial

**Notes**:
_______________________________________________
_______________________________________________
_______________________________________________

## Success Criteria

The system passes testing if:
- [ ] All 7 agents display correctly
- [ ] All 6 programs display correctly
- [ ] Purchase flow completes successfully
- [ ] Rental flow completes successfully
- [ ] Enrollment flow completes successfully
- [ ] No critical console errors
- [ ] All API endpoints return 200 status
- [ ] Responsive design works on all screen sizes
- [ ] Navigation works correctly
- [ ] All modals open and close properly

## Next Steps After Testing

1. Document any bugs found
2. Fix critical issues
3. Re-test affected features
4. Proceed with deployment to production
5. Set up monitoring and logging

---

**Testing Complete!** 🎉

If all tests pass, the Neo3 system is ready for production deployment.
