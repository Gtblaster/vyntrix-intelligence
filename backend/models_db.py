from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), default="user") # 'admin', 'user'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50), index=True)
    endpoint = Column(String(200))
    method = Column(String(10))
    payload_snippet = Column(Text, nullable=True)
    
    # AI/Detection Metadata
    risk_score = Column(Float, default=0.0)
    is_blocked = Column(Boolean, default=False)
    threat_type = Column(String(100), nullable=True)
    xai_explanation = Column(Text, nullable=True) # SHAP human readable output
    
    # Adding for Roadmap Scalability
    request_id = Column(String(100), unique=True, index=True, nullable=True)
    shap_json = Column(Text, nullable=True) # Granular SHAP feature importance mapping

class WebhookConfig(Base):
    __tablename__ = "webhook_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class VirtualPatch(Base):
    """
    Simulates a generated WAF physical IP block (Phase 4 Self-Healing)
    """
    __tablename__ = "virtual_patches"

    id = Column(Integer, primary_key=True, index=True)
    target_ip = Column(String(50), unique=True, index=True, nullable=False)
    reason = Column(Text) # "Repeated SQLi attempts on /secure-login"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expiration = Column(DateTime(timezone=True), nullable=True) # Optional TTL

class ThreatIntelIOC(Base):
    """
    Stores structured indicators of compromise (IoC) synced from MISP/STIX feeds.
    """
    __tablename__ = "threat_intel_iocs"

    id = Column(Integer, primary_key=True, index=True)
    indicator = Column(String(255), unique=True, index=True, nullable=False) # e.g., bad IP, bad hash
    indicator_type = Column(String(50), nullable=False) # 'ipv4-addr', 'url', 'file:hashes'
    risk_level = Column(Integer, default=50) # 0 to 100
    source = Column(String(100), default="Internal") # 'MISP', 'OTX'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
