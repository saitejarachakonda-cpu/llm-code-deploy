# server/app.py
import os
import tempfile
import base64
import pathlib
import json
import subprocess
from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
from .generator import generate_app_from_request
from .git_utils import create_and_push_repo
app = FastAPI()
STORED_SECRET = os.environ.get("STORED_SECRET")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORG = os.environ.get("GITHUB_ORG") # optional

class ProjectRequest(BaseModel):   
  email: str   
  secret: str   
  task: str  
  round: int   
  nonce: str   
  brief: str  
  checks: list[str] = []  
  evaluation_url: str  
  attachments: list[Dict[str, Any]] = []

@app.post("/api-endpoint")
async def receive_request(req: Request):   
  body = await req.json()  
  # Validate  
  try:      
    payload = ProjectRequest(**body)   
  except Exception as e:     
    raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
  if STORED_SECRET is None:       
      raise HTTPException(status_code=500, detail="Server secret not configured")
  if payload.secret != STORED_SECRET:  
    raise HTTPException(status_code=403, detail="Invalid secret")
    # respond 200 quickly but then do heavy work synchronously (per project rules)    # Send immediate 200    # But we still perform the generation and callback in this request (must succeed within 10 minutes)
    # Create temp dir for app   
  tmpdir = tempfile.mkdtemp(prefix="tds_")
    # generate the minimal app   
  try:      
    generate_app_from_request(payload, tmpdir) 
  except Exception as e:     
    raise HTTPException(status_code=500, detail=f"Generator failed: {e}")
    # create git repo and push   
  try:     
    repo_info = create_and_push_repo(
      local_dir=tmpdir,           
      task_name=payload.task,        
      github_token=os.environ.get("GITHUB_TOKEN"),       
      org=os.environ.get("GITHUB_ORG"),      
    )   
  except Exception as e:  
    raise HTTPException(status_code=500, detail=f"GitHub push failed: {e}")
    # Post to evaluation_url  
  callback_payload = {   
    "email": payload.email,   
    "task": payload.task,  
    "round": payload.round,  
    "nonce": payload.nonce, 
    "repo_url": repo_info["repo_url"],     
    "commit_sha": repo_info["commit_sha"],  
    "pages_url": repo_info["pages_url"],   
  }
    headers = {"Content-Type": "application/json"} 
    try:   
      r = requests.post(payload.evaluation_url, json=callback_payload, headers=headers, timeout=30)
      r.raise_for_status()  
    except Exception as e:  
      raise HTTPException(status_code=500, detail=f"Callback to evaluation_url failed: {e}")
    return {"status": "ok", "repo": repo_info}
