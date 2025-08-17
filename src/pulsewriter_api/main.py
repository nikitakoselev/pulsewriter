from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pulsewriter_core import TransformConfig, generate, revise

app = FastAPI(title="PulseWriter API", version="0.1.0")

class GenerateRequest(BaseModel):
    topic: Optional[str] = None
    body_markdown: Optional[str] = None
    persona: str = "action-oriented"
    tone: str = "practical"
    platforms: List[str] = ["blog","linkedin","x"]
    word_target: int = 600

class GenerateResponse(BaseModel):
    draft_id: str
    outputs: Dict[str, str]
    summary: str

class ReviseRequest(BaseModel):
    draft_id: str
    instructions: str
    targets: Optional[List[str]] = None
    drafts: Dict[str, str]

@app.post("/generate", response_model=GenerateResponse)
def post_generate(req: GenerateRequest):
    # In a real system, you'd expand topic -> outline -> body; here we pass through body_markdown
    body = req.body_markdown or f"""{req.topic or 'New Post Idea'}\n\n- Why it matters\n- What to do today\n- How it compounds"""
    cfg = TransformConfig(tone=req.tone, persona=req.persona, word_target=req.word_target)
    outs = generate(body, req.platforms, cfg)
    # naive summary — first line of body
    summary = (body.splitlines()[0] if body else "Draft")
    return {"draft_id": "draft-001", "outputs": outs, "summary": summary}

@app.post("/revise")
def post_revise(req: ReviseRequest):
    revised = revise(req.drafts, req.instructions)
    return {"draft_id": req.draft_id, "outputs": revised}
