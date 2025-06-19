from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from shapely.geometry import Point
from shapely.wkt import loads as wkt_loads
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
DB_NAME = os.getenv("DB_NAME", "msr_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# データベースモデル
class ServiceSpecification(Base):
    __tablename__ = "service_specifications"
    
    mrn = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    keywords = Column(JSON)
    status = Column(String, default="draft")
    organization_mrn = Column(String, nullable=False, index=True)
    specification_document = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    service_instances = relationship("ServiceInstance", back_populates="service_specification")

class ServiceInstance(Base):
    __tablename__ = "service_instances"
    
    mrn = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    service_specification_mrn = Column(String, ForeignKey("service_specifications.mrn"), nullable=False, index=True)
    organization_mrn = Column(String, nullable=False, index=True)
    endpoint_uri = Column(String, nullable=False)
    endpoint_type = Column(String, default="REST")
    status = Column(String, default="active")
    coverage_area_wkt = Column(Text)
    bbox_min_lat = Column(Float)
    bbox_max_lat = Column(Float)
    bbox_min_lng = Column(Float)
    bbox_max_lng = Column(Float)
    service_metadata = Column(JSON)
    last_health_check = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    service_specification = relationship("ServiceSpecification", back_populates="service_instances")

# Pydanticスキーマ
class ServiceSpecificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    keywords: Optional[List[str]] = []
    status: str = "draft"
    organization_mrn: str = Field(..., pattern=r"^urn:mrn:mcp:org:")
    specification_document: Optional[str] = None

class ServiceSpecificationCreate(ServiceSpecificationBase):
    mrn: str = Field(..., pattern=r"^urn:mrn:mcp:service:")

class ServiceSpecificationResponse(ServiceSpecificationBase):
    mrn: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ServiceInstanceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    service_specification_mrn: str = Field(..., pattern=r"^urn:mrn:mcp:service:")
    organization_mrn: str = Field(..., pattern=r"^urn:mrn:mcp:org:")
    endpoint_uri: str = Field(..., min_length=1)
    endpoint_type: str = "REST"
    status: str = "active"
    coverage_area_wkt: Optional[str] = None
    service_metadata: Optional[Dict[str, Any]] = {}

class ServiceInstanceCreate(ServiceInstanceBase):
    mrn: str = Field(..., pattern=r"^urn:mrn:mcp:instance:")

class ServiceInstanceResponse(ServiceInstanceBase):
    mrn: str
    bbox_min_lat: Optional[float] = None
    bbox_max_lat: Optional[float] = None
    bbox_min_lng: Optional[float] = None
    bbox_max_lng: Optional[float] = None
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# FastAPIアプリケーション
app = FastAPI(
    title="MCP Maritime Service Registry (Demo)",
    description="Demo version of MCP Service Registry",
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

# 地理空間ユーティリティ
def calculate_bbox(wkt_string: str):
    """WKT文字列から境界ボックスを計算"""
    try:
        geometry = wkt_loads(wkt_string)
        bounds = geometry.bounds
        return bounds  # (min_lng, min_lat, max_lng, max_lat)
    except:
        return None

# テーブル作成
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("MSR Demo service started")

# API エンドポイント
@app.get("/health")
async def health_check():
    return {"status": "UP", "service": "MSR", "timestamp": datetime.utcnow()}

# サービス仕様関連
@app.get("/api/v1/serviceSpecifications")
async def get_service_specifications(
    skip: int = 0,
    limit: int = 100,
    organization_mrn: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """サービス仕様一覧を取得"""
    query = db.query(ServiceSpecification)
    
    if organization_mrn:
        query = query.filter(ServiceSpecification.organization_mrn == organization_mrn)
    if status:
        query = query.filter(ServiceSpecification.status == status)
    
    total = query.count()
    specifications = query.offset(skip).limit(limit).all()
    
    return {"count": total, "specifications": specifications}

@app.get("/api/v1/serviceSpecifications/{mrn}", response_model=ServiceSpecificationResponse)
async def get_service_specification(mrn: str, db: Session = Depends(get_db)):
    """特定のサービス仕様を取得"""
    spec = db.query(ServiceSpecification).filter(ServiceSpecification.mrn == mrn).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Service specification not found")
    return spec

@app.post("/api/v1/serviceSpecifications", response_model=ServiceSpecificationResponse, status_code=201)
async def create_service_specification(
    spec: ServiceSpecificationCreate,
    db: Session = Depends(get_db)
):
    """新しいサービス仕様を作成"""
    existing = db.query(ServiceSpecification).filter(ServiceSpecification.mrn == spec.mrn).first()
    if existing:
        raise HTTPException(status_code=409, detail="Service specification already exists")
    
    db_spec = ServiceSpecification(**spec.dict())
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    
    logger.info(f"Created service specification: {spec.mrn}")
    return db_spec

# サービスインスタンス関連
@app.get("/api/v1/serviceInstances")
async def get_service_instances(
    skip: int = 0,
    limit: int = 100,
    organization_mrn: Optional[str] = None,
    status: str = "active",
    db: Session = Depends(get_db)
):
    """サービスインスタンス一覧を取得"""
    query = db.query(ServiceInstance)
    
    if organization_mrn:
        query = query.filter(ServiceInstance.organization_mrn == organization_mrn)
    
    query = query.filter(ServiceInstance.status == status)
    
    total = query.count()
    instances = query.offset(skip).limit(limit).all()
    
    return {"count": total, "instances": instances}

@app.get("/api/v1/serviceInstances/{mrn}", response_model=ServiceInstanceResponse)
async def get_service_instance(mrn: str, db: Session = Depends(get_db)):
    """特定のサービスインスタンスを取得"""
    instance = db.query(ServiceInstance).filter(ServiceInstance.mrn == mrn).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Service instance not found")
    return instance

@app.post("/api/v1/serviceInstances", response_model=ServiceInstanceResponse, status_code=201)
async def create_service_instance(
    instance: ServiceInstanceCreate,
    db: Session = Depends(get_db)
):
    """新しいサービスインスタンスを作成"""
    existing = db.query(ServiceInstance).filter(ServiceInstance.mrn == instance.mrn).first()
    if existing:
        raise HTTPException(status_code=409, detail="Service instance already exists")
    
    # サービス仕様の存在確認
    spec = db.query(ServiceSpecification).filter(
        ServiceSpecification.mrn == instance.service_specification_mrn
    ).first()
    if not spec:
        raise HTTPException(status_code=400, detail="Service specification not found")
    
    db_instance = ServiceInstance(**instance.dict())
    
    # 境界ボックスを計算
    if instance.coverage_area_wkt:
        bbox = calculate_bbox(instance.coverage_area_wkt)
        if bbox:
            db_instance.bbox_min_lng = bbox[0]
            db_instance.bbox_min_lat = bbox[1] 
            db_instance.bbox_max_lng = bbox[2]
            db_instance.bbox_max_lat = bbox[3]
    
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    
    logger.info(f"Created service instance: {instance.mrn}")
    return db_instance

# 検索関連
@app.get("/api/v1/search/services")
async def search_services(
    keywords: Optional[str] = Query(None, description="検索キーワード"),
    organization_mrn: Optional[str] = Query(None, description="組織MRN"),
    location: Optional[str] = Query(None, description="位置（lng,lat形式）"),
    radius: Optional[float] = Query(None, description="検索半径（km）"),
    status: str = Query("active", description="インスタンスステータス"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """サービスインスタンスを検索"""
    
    query = db.query(ServiceInstance)
    
    # ステータスフィルタ
    query = query.filter(ServiceInstance.status == status)
    
    # 組織フィルタ
    if organization_mrn:
        query = query.filter(ServiceInstance.organization_mrn == organization_mrn)
    
    # キーワード検索
    if keywords:
        spec_query = db.query(ServiceSpecification.mrn).filter(
            ServiceSpecification.name.ilike(f"%{keywords}%")
        )
        spec_mrns = [spec.mrn for spec in spec_query.all()]
        if spec_mrns:
            query = query.filter(ServiceInstance.service_specification_mrn.in_(spec_mrns))
        else:
            # キーワードにマッチするサービス仕様がない場合
            return {"count": 0, "services": []}
    
    # 地理的検索（簡易版）
    if location and radius:
        try:
            lng, lat = map(float, location.split(','))
            lat_delta = radius / 111.0  # 1度 ≈ 111km
            lng_delta = radius / (111.0 * abs(lat))
            
            query = query.filter(
                ServiceInstance.bbox_min_lat <= lat + lat_delta,
                ServiceInstance.bbox_max_lat >= lat - lat_delta,
                ServiceInstance.bbox_min_lng <= lng + lng_delta,
                ServiceInstance.bbox_max_lng >= lng - lng_delta
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid location format")
    
    total = query.count()
    instances = query.offset(skip).limit(limit).all()
    
    return {"count": total, "services": instances}

@app.get("/api/v1/search/specifications")
async def search_specifications(
    keywords: Optional[str] = Query(None),
    organization_mrn: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """サービス仕様を検索"""
    
    query = db.query(ServiceSpecification)
    
    if organization_mrn:
        query = query.filter(ServiceSpecification.organization_mrn == organization_mrn)
    
    if status:
        query = query.filter(ServiceSpecification.status == status)
    
    if keywords:
        query = query.filter(
            ServiceSpecification.name.ilike(f"%{keywords}%")
        )
    
    total = query.count()
    specifications = query.offset(skip).limit(limit).all()
    
    return {"count": total, "specifications": specifications}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)