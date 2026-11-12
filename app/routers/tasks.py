from fastapi import APIRouter, HTTPException

from app import cpu_tasks, io_tasks
from app.schemas import TaskResult

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/list")
def list_tasks():
    return {"cpu": list(cpu_tasks.TASKS), "io": list(io_tasks.TASKS)}


@router.get("/cpu/{name}", response_model=TaskResult)
def run_cpu_task(name: str):
    try:
        return cpu_tasks.run(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/io/{name}", response_model=TaskResult)
def run_io_task(name: str):
    try:
        return io_tasks.run(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/mixed")
def run_mixed():
    """Fire every hard task once, back to back -- a one-shot stress test
    endpoint that's convenient to point a profiler or locust at."""
    results = []
    for name in cpu_tasks.TASKS:
        results.append(cpu_tasks.run(name))
    for name in io_tasks.TASKS:
        results.append(io_tasks.run(name))
    return {"results": results}
