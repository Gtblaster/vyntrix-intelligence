from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import re
import datetime
import asyncio

import database
import models_db
import auth
import webhooks
import self_healing
from model import predict_image, predict_text

# Initialize Database
models_db.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Vyntrix Intelligence Enterprise Endpoint")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------
# Signature Engine Middleware (Phase 1)
# -----------------
@app.middleware("http")
async def signature_engine_middleware(request: Request, call_next):
    # Basic Signature Rules
    SIGNATURE_RULES = [
        re.compile(r"(?i)(<script>|javascript:|alert\()"),        # XSS
        re.compile(r"(?i)(union\s+select|or\s+1=1|drop\s+table)"), # SQLi
        re.compile(r"(?i)(\.\./\.\./)")                            # Path Traversal
    ]
    
    # 1. Skip on non-critical routes for MVP speed, or apply to all.
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    # Check if IP is blocked by Virtual Patch (Self-Healing - Phase 4)
    db = database.SessionLocal()
    try:
        if client_ip != "unknown":
            patch = db.query(models_db.VirtualPatch).filter(
                models_db.VirtualPatch.target_ip == client_ip,
                models_db.VirtualPatch.is_active == True
            ).first()
            if patch:
                return JSONResponse(status_code=403, content={"detail": f"Access Denied: Virtual Patch Active. Reason: {patch.reason}"})

        # Check Signatures on URL/Query params
        qs = request.url.query.decode("utf-8") if request.url.query else ""
        for rule in SIGNATURE_RULES:
            if rule.search(qs) or rule.search(path):
                # Log the blocked attempt
                log = models_db.RequestLog(
                    ip_address=client_ip,
                    endpoint=path,
                    method=request.method,
                    payload_snippet=f"QueryString match: {qs}",
                    is_blocked=True,
                    threat_type="Signature Match (XSS/SQLi)"
                )
                db.add(log)
                db.commit()
                return JSONResponse(status_code=403, content={"detail": "Request blocked by WAF Edge (Signature Match)"})
    finally:
        db.close()
        
    response = await call_next(request)
    return response


# -----------------
# Authentication (Phase 1)
# -----------------
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models_db.User).filter(models_db.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/register", status_code=201)
def create_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Note: Using form_data.username/password for simple registration. In a real app we'd use a custom BaseModel
    user_exists = db.query(models_db.User).filter(models_db.User.username == form_data.username).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_password = auth.get_password_hash(form_data.password)
    new_user = models_db.User(username=form_data.username, email=f"{form_data.username}@example.com", hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

# -----------------
# Core AI Endpoints (Phase 2 & 4)
# -----------------

from fastapi import UploadFile, File

@app.post("/scan-image/")
async def scan_image(file: UploadFile = File(...), db: Session = Depends(database.get_db), req: Request = None):
    # Existing image logic
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    image_bytes = await file.read()
    prediction_result = predict_image(image_bytes)
    
    if not prediction_result.get("success"):
        raise HTTPException(status_code=500, detail=prediction_result.get('error'))
        
    return prediction_result

class TextInput(BaseModel):
    text: str

@app.post("/scan-text/")
async def scan_text(payload: TextInput, db: Session = Depends(database.get_db), req: Request = None):
    if len(payload.text) > 5000:
         raise HTTPException(status_code=400, detail="Payload too large. Max 5000 characters.")
         
    prediction_result = predict_text(payload.text)
    
    if not prediction_result.get("success"):
        raise HTTPException(status_code=500, detail=prediction_result.get('error'))
        
    # Log the payload logic (Self-Healing & Webhook Integration)
    client_ip = req.client.host if req and req.client else "unknown"
    risk_score = prediction_result.get("threat_probability", 0.0)
    is_malicious = prediction_result.get("is_malicious", False)
    
    log = models_db.RequestLog(
        ip_address=client_ip,
        endpoint="/scan-text/",
        method="POST",
        payload_snippet=payload.text[:100], # Keep a snippet for DB limits
        risk_score=risk_score,
        is_blocked=is_malicious,
        threat_type=prediction_result.get("ai_classification"),
        xai_explanation=prediction_result.get("shap_explanation")
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    # Self-Healing Pipeline
    if is_malicious and risk_score > 80.0:
        # Generate Virtual Patch if needed
        patch = self_healing.check_and_generate_virtual_patch(db, client_ip)
        
        # Fire Webhooks
        asyncio.create_task(webhooks.dispatch_webhook_alert(db, log))
        
    return prediction_result


class ContactInput(BaseModel):
    name: str
    email: str
    message: str

@app.post("/contact/")
async def submit_contact(payload: ContactInput):
    # Existing simplistic logic intact to prevent breaking the web app's current setup.
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] Name: {payload.name} | Email: {payload.email} | Message: {payload.message}"
    with open("contacts.db", "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    return {"success": True, "message": "Contact saved successfully."}

# -----------------
# Developer Ecosystem (Phase 3)
# -----------------
class WebhookInput(BaseModel):
    name: str
    url: str

@app.post("/webhooks/register")
def register_webhook(webhook: WebhookInput, db: Session = Depends(database.get_db), current_user: models_db.User = Depends(auth.get_current_user)):
    new_hook = models_db.WebhookConfig(name=webhook.name, url=webhook.url)
    db.add(new_hook)
    db.commit()
    db.refresh(new_hook)
    return {"message": "Webhook registered", "id": new_hook.id}
    
@app.get("/system/status")
def system_status(db: Session = Depends(database.get_db), current_user: models_db.User = Depends(auth.get_current_user)):
    return {"status": "Enterprise Endpoint Active", "user": current_user.username}
