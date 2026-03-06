from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
import time

from solver import find_solution

app = FastAPI(title="Countdown Solver API")

# ✅ IMPORTANT: set this to your GitHub Pages origin
# Example: https://arjunjanamatti217-ship-it.github.io
ALLOWED_ORIGINS = [
    "https://arjunjanamatti217-ship-it.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # allows your GH Pages frontend to call backend
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckRequest(BaseModel):
    numbers: List[int] = Field(..., min_length=2, max_length=10)
    target: int
    time_limit: float = Field(1.0, ge=0.05, le=10.0)

class CheckResponse(BaseModel):
    solvable: bool
    token: str
    computed_ms: int

class SolveRequest(BaseModel):
    numbers: List[int] = Field(..., min_length=2, max_length=10)
    target: int
    token: str
    time_limit: float = Field(2.0, ge=0.05, le=20.0)

class SolveResponse(BaseModel):
    solvable: bool
    steps: Optional[List[str]] = None
    computed_ms: int

# lightweight token gate: solution is only returned if user calls /solve with the token
TOKENS = {}  # token -> (sorted_numbers_tuple, target)

@app.post("/check", response_model=CheckResponse)
def check(req: CheckRequest):
    t0 = time.time()
    steps = find_solution(req.numbers, req.target, time_limit=req.time_limit)

    token = str(uuid.uuid4())
    TOKENS[token] = (tuple(sorted(req.numbers)), req.target)

    return CheckResponse(
        solvable=steps is not None,
        token=token,
        computed_ms=int((time.time() - t0) * 1000),
    )

@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    t0 = time.time()
    key = TOKENS.get(req.token)

    # token mismatch => refuse reveal
    if key is None or key != (tuple(sorted(req.numbers)), req.target):
        return SolveResponse(solvable=False, steps=None, computed_ms=int((time.time() - t0) * 1000))

    steps = find_solution(req.numbers, req.target, time_limit=req.time_limit)
    return SolveResponse(
        solvable=steps is not None,
        steps=steps,
        computed_ms=int((time.time() - t0) * 1000),
    )
