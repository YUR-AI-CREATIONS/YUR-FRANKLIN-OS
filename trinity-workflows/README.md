# Trinity Orchestration Integration for Franklin OS

**Lean & Mean Multi-Agent Coordination**

## Overview

Trinity provides dependency-aware task orchestration for Franklin OS agents. It replaces custom orchestrators with declarative YAML workflows.

## Quick Start

```bash
# Validate workflow
run-trinity.bat agent-mission-executor validate

# Dry-run (see what would execute)
run-trinity.bat agent-mission-executor dry-run

# Execute mission
run-trinity.bat agent-mission-executor run MISSION_123
```

## Available Workflows

### 1. agent-mission-executor.yaml
**Purpose:** Orchestrate multi-agent missions with parallel execution  
**Agents:** Legal, Financial, Technical  
**Concurrency:** 3 agents simultaneously  
**Usage:**
```bash
run-trinity.bat agent-mission-executor run MISSION_ID_HERE
```

### 2. agent-team-coordination.yaml
**Purpose:** Coordinate agent teams for complex projects  
**Agents:** Legal, Financial, Technical, Marketing  
**Concurrency:** 2 agents simultaneously (resource throttling)  
**Usage:**
```bash
set PROJECT_ID=PROJECT_123
run-trinity.bat agent-team-coordination run
```

### 3. agent-training-pipeline.yaml
**Purpose:** Train, evaluate, and certify agents  
**Mode:** Sequential (prevents resource conflicts)  
**Usage:**
```bash
set AGENT_NAME=legal_agent
set BASE_MODEL=gpt-4
run-trinity.bat agent-training-pipeline run
```

### 4. service-integration-pipeline.yaml
**Purpose:** Start and verify all backend services  
**Concurrency:** 4 services simultaneously  
**Usage:**
```bash
run-trinity.bat service-integration-pipeline run
```

## Key Features

✅ **Dependency Management** - Tasks execute in correct order automatically  
✅ **Parallel Execution** - Multiple agents run simultaneously (configurable)  
✅ **Error Handling** - Task failures stop dependent tasks  
✅ **Environment Variables** - Dynamic configuration per execution  
✅ **Dry-Run Mode** - Test workflows without execution  

## Integration Architecture

```
Franklin OS
├── Superagents/          → Agent implementations (unchanged)
├── services/             → Coordination services (unchanged)
├── backend/              → Core backend (unchanged)
└── trinity-workflows/    → Trinity orchestration (NEW)
    ├── *.yaml            → Workflow definitions
    └── run-trinity.bat   → Executor script
```

**What Changed:** Added workflow orchestration layer  
**What Stayed:** All agent logic, services, and backend code

## Creating Custom Workflows

```yaml
name: my-custom-workflow
description: What this workflow does

config:
  concurrency: 2  # Max parallel tasks

tasks:
  task-one:
    command: python ../path/to/script.py --arg value
    description: What this task does
    env:
      VAR_NAME: ${VAR_NAME}
  
  task-two:
    command: python ../path/to/another.py
    description: Runs after task-one
    depends_on: [task-one]
```

## Workflow Modes

- **validate** - Check workflow syntax and dependencies
- **dry-run** - Show execution plan without running commands
- **run** - Execute workflow tasks

## Environment Variables

Pass variables to workflows:
```bash
set MISSION_ID=MISSION_123
set AGENT_MODE=production
run-trinity.bat agent-mission-executor run
```

Variables in workflow:
```yaml
env:
  MISSION_ID: ${MISSION_ID}
  AGENT_MODE: ${AGENT_MODE:-development}  # default value
```

## Monitoring & Debugging

Trinity outputs task status in real-time:
```
[OK] initialize-mission
[OK] legal-agent-analyze
[OK] financial-agent-assess
[OK] technical-agent-plan
[OK] coordination-synthesis
```

Failed tasks show:
```
[X] task-name: Error message here
```

## Next Steps

1. **Test workflows in dry-run mode first**
   ```bash
   run-trinity.bat agent-mission-executor dry-run
   ```

2. **Customize for your agents**
   - Edit workflow YAML files
   - Adjust concurrency limits
   - Add your agent scripts

3. **Integrate with existing code**
   - Call `run-trinity.bat` from Python:
     ```python
     import subprocess
     result = subprocess.run([
         'trinity-workflows/run-trinity.bat',
         'agent-mission-executor',
         'run',
         mission_id
     ])
     ```

## Why Trinity?

| Custom Orchestrator | Trinity |
|---------------------|---------|
| Python code for dependencies | YAML declarations |
| Manual parallelism | Automatic concurrency |
| Hard to visualize flow | Clear workflow graph |
| Scattered error handling | Centralized management |
| Testing is complex | Built-in dry-run mode |

## Links

- Trinity Repository: https://github.com/jag0414/Trinity-
- Trinity Documentation: See LIVE_TESTING_GUIDE.md in Trinity repo
- All tests passing: 20/20 on Windows

---

**Status:** Production-ready  
**Last Updated:** 2026-02-22  
**Integration:** Lean & Mean ✅
