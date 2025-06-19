from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "mcp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mcp123")
DB_NAME = os.getenv("DB_NAME", "mir_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# データベースモデル
class Organization(Base):
    __tablename__ = "organizations"
    
    mrn = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    description = Column(Text)
    contact_email = Column(String)
    website = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydanticスキーマ
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., min_length=2, max_length=3)
    description: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    mrn: str = Field(..., pattern=r"^urn:mrn:mcp:org:")

class OrganizationResponse(OrganizationBase):
    mrn: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationList(BaseModel):
    count: int
    organizations: List[OrganizationResponse]

# FastAPIアプリケーション
app = FastAPI(
    title="MCP Maritime Identity Registry (Demo)",
    description="Demo version of MCP Identity Registry",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# テーブル作成
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("MIR Demo service started")

# API エンドポイント
@app.get("/health")
async def health_check():
    return {"status": "UP", "service": "MIR", "timestamp": datetime.utcnow()}

@app.get("/api/v1/organizations", response_model=OrganizationList)
async def get_organizations(
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """組織一覧を取得"""
    query = db.query(Organization)
    
    if country:
        query = query.filter(Organization.country == country)
    
    total = query.count()
    organizations = query.offset(skip).limit(limit).all()
    
    return OrganizationList(count=total, organizations=organizations)

@app.get("/api/v1/organizations/{mrn}", response_model=OrganizationResponse)
async def get_organization(mrn: str, db: Session = Depends(get_db)):
    """特定の組織を取得"""
    organization = db.query(Organization).filter(Organization.mrn == mrn).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization

@app.post("/api/v1/organizations", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """新しい組織を作成"""
    # 既存チェック
    existing = db.query(Organization).filter(Organization.mrn == organization.mrn).first()
    if existing:
        raise HTTPException(status_code=409, detail="Organization already exists")
    
    db_organization = Organization(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    
    logger.info(f"Created organization: {organization.mrn}")
    return db_organization

@app.put("/api/v1/organizations/{mrn}", response_model=OrganizationResponse)
async def update_organization(
    mrn: str,
    organization: OrganizationBase,
    db: Session = Depends(get_db)
):
    """組織情報を更新"""
    db_organization = db.query(Organization).filter(Organization.mrn == mrn).first()
    if not db_organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    for field, value in organization.dict(exclude_unset=True).items():
        setattr(db_organization, field, value)
    
    db_organization.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_organization)
    
    logger.info(f"Updated organization: {mrn}")
    return db_organization

@app.delete("/api/v1/organizations/{mrn}", status_code=204)
async def delete_organization(mrn: str, db: Session = Depends(get_db)):
    """組織を削除"""
    db_organization = db.query(Organization).filter(Organization.mrn == mrn).first()
    if not db_organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    db.delete(db_organization)
    db.commit()
    
    logger.info(f"Deleted organization: {mrn}")

# 証明書関連のシンプルなエンドポイント（デモ用）
@app.get("/api/v1/certificates")
async def get_certificates():
    """証明書一覧を取得（デモ用）"""
    return {
        "count": 3,
        "certificates": [
            {
                "id": "cert-001",
                "mrn": "urn:mrn:mcp:org:demo:maritime-authority",
                "subject": "CN=Demo Maritime Authority",
                "issuer": "CN=MCP Demo CA",
                "valid_from": "2024-01-01T00:00:00Z",
                "valid_to": "2025-01-01T00:00:00Z",
                "status": "active"
            },
            {
                "id": "cert-002", 
                "mrn": "urn:mrn:mcp:org:demo:shipping-company",
                "subject": "CN=Demo Shipping Company",
                "issuer": "CN=MCP Demo CA",
                "valid_from": "2024-01-01T00:00:00Z",
                "valid_to": "2025-01-01T00:00:00Z",
                "status": "active"
            },
            {
                "id": "cert-003",
                "mrn": "urn:mrn:mcp:org:demo:port-authority", 
                "subject": "CN=Demo Port Authority",
                "issuer": "CN=MCP Demo CA",
                "valid_from": "2024-01-01T00:00:00Z",
                "valid_to": "2025-01-01T00:00:00Z",
                "status": "active"
            }
        ]
    }

@app.post("/api/v1/certificates")
async def create_certificate():
    """証明書を作成（デモ用）"""
    return {
        "message": "Certificate created successfully (demo)",
        "certificate_id": "cert-demo-001",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)