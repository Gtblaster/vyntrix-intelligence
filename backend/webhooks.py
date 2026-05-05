import httpx
from sqlalchemy.orm import Session
import models_db
import asyncio

async def dispatch_webhook_alert(db: Session, request_log: models_db.RequestLog):
    """
    Simulates sending a webhook alert for a critical severity threat/block.
    Hits all active configurations in the WebhookConfig table.
    """
    configs = db.query(models_db.WebhookConfig).filter(models_db.WebhookConfig.is_active == True).all()
    
    if not configs:
        return # No active webhooks
        
    payload = {
        "event": "vyntrix_threat_blocked",
        "severity": "CRITICAL" if request_log.risk_score > 85.0 else "WARNING",
        "ip_address": request_log.ip_address,
        "threat_type": request_log.threat_type,
        "xai_explanation": request_log.xai_explanation,
        "timestamp": str(request_log.timestamp)
    }
    
    # Normally we use celery or a message broker. For MVPs we use asyncio.create_task in main.
    async with httpx.AsyncClient() as client:
        for config in configs:
            try:
                # Dispatching asynchronously to not block the main API response
                await client.post(config.url, json=payload, timeout=2.0)
                print(f"[Webhook Manager] Alert sent to {config.name} ({config.url})")
            except Exception as e:
                print(f"[Webhook Manager] Failed to send alert to {config.name}: {e}")

