from sqlalchemy.orm import Session
import models_db
from datetime import datetime, timedelta

def check_and_generate_virtual_patch(db: Session, ip_address: str):
    """
    Simulates the Self-Healing process. 
    If an IP exceeds 3 high-risk attacks within 10 minutes, we create a VirtualPatch.
    """
    if not ip_address:
        return None
        
    # Check if a patch already exists for this IP
    existing_patch = db.query(models_db.VirtualPatch).filter(
        models_db.VirtualPatch.target_ip == ip_address,
        models_db.VirtualPatch.is_active == True
    ).first()
    
    if existing_patch:
        return existing_patch
        
    time_threshold = datetime.utcnow() - timedelta(minutes=10)
    
    # Count how many critical attacks this IP has produced recently
    recent_attacks = db.query(models_db.RequestLog).filter(
        models_db.RequestLog.ip_address == ip_address,
        models_db.RequestLog.timestamp >= time_threshold,
        models_db.RequestLog.risk_score > 80.0
    ).count()
    
    if recent_attacks >= 3:
        reason = f"Automated Self-Healing: Triggered by {recent_attacks} critical alerts (Risk > 80) in the last 10 minutes."
        print(f"[Self-Healing] Generating Virtual Patch for IP: {ip_address}")
        
        # Deploy "Virtual Patch"
        patch = models_db.VirtualPatch(
            target_ip=ip_address,
            reason=reason,
            expiration=datetime.utcnow() + timedelta(hours=24) # 24h block
        )
        db.add(patch)
        db.commit()
        db.refresh(patch)
        return patch
        
    return None
