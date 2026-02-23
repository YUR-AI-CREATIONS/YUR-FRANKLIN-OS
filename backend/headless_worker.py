import asyncio
import uuid
import logging
from typing import Dict, Any, Optional

from franklin_realtime import broker
from sentinel_guard import check_code_safety
from simple_build import simple_build

logger = logging.getLogger(__name__)

# Lightweight in-memory queue/registry
job_queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue()
jobs: Dict[str, Dict[str, Any]] = {}


async def worker_loop():
    while True:
        job = await job_queue.get()
        job_id = job["job_id"]
        try:
            await broker.push(job["project_id"], {
                "type": "headless_status",
                "status": "started",
                "job_id": job_id,
                "agent_id": job.get("agent_id"),
                "contract": job.get("contract"),
            })
            result = await run_job(job)
            jobs[job_id]["result"] = result
            jobs[job_id]["status"] = "completed" if result.get("success") else "error"
            await broker.push(job["project_id"], {
                "type": "headless_status",
                "status": jobs[job_id]["status"],
                "job_id": job_id,
                "agent_id": job.get("agent_id"),
                "build_id": result.get("build_id"),
                "error": result.get("error"),
            })
        except Exception as e:
            logger.exception("Headless job failed: %s", e)
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
            await broker.push(job["project_id"], {
                "type": "headless_status",
                "status": "error",
                "job_id": job_id,
                "error": str(e),
            })
        finally:
            job_queue.task_done()


async def run_job(job: Dict[str, Any]) -> Dict[str, Any]:
    prompt = job["prompt"]
    retries = 2
    last_error: Optional[str] = None
    for attempt in range(retries + 1):
        try:
            result = await simple_build.build(prompt)
            if not result.get("success"):
                last_error = result.get("error", "build failed")
                continue
            ok, issues = check_code_safety(result.get("file_contents", {}))
            if not ok:
                last_error = "; ".join(issues)
                continue
            return {**result, "success": True}
        except Exception as e:
            last_error = str(e)
            continue
    return {"success": False, "error": last_error}


def enqueue_job(prompt: str, project_id: str, agent_id: Optional[str], contract: Optional[Dict[str, Any]]) -> str:
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "prompt": prompt,
        "project_id": project_id,
        "agent_id": agent_id,
        "contract": contract,
        "status": "queued",
    }
    jobs[job_id] = job
    job_queue.put_nowait(job)
    return job_id


# start worker
def start_worker(loop: asyncio.AbstractEventLoop):
    loop.create_task(worker_loop())
