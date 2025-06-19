-- Keycloak用データベース
CREATE DATABASE keycloak;

-- MIR用データベース
CREATE DATABASE mir_db;

-- MSR用データベース
CREATE DATABASE msr_db;

-- 各データベースに必要な拡張機能
\c mir_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\c msr_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis"; -- 地理空間データ用

-- デモ用ユーザーとデータの作成
\c mir_db;

-- 組織テーブル
CREATE TABLE IF NOT EXISTS organizations (
    mrn VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    description TEXT,
    contact_email VARCHAR,
    website VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- デモ組織データ
INSERT INTO organizations (mrn, name, country, description, contact_email) VALUES
('urn:mrn:mcp:org:demo:maritime-authority', 'Demo Maritime Authority', 'JP', 'Demo maritime authority organization', 'contact@demo-maritime.com'),
('urn:mrn:mcp:org:demo:shipping-company', 'Demo Shipping Company', 'JP', 'Demo shipping company', 'info@demo-shipping.com'),
('urn:mrn:mcp:org:demo:port-authority', 'Demo Port Authority', 'JP', 'Demo port authority', 'port@demo-authority.com');

\c msr_db;

-- サービス仕様テーブル
CREATE TABLE IF NOT EXISTS service_specifications (
    mrn VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    description TEXT NOT NULL,
    keywords JSON,
    status VARCHAR DEFAULT 'draft',
    organization_mrn VARCHAR NOT NULL,
    specification_document TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- サービスインスタンステーブル
CREATE TABLE IF NOT EXISTS service_instances (
    mrn VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL,
    service_specification_mrn VARCHAR NOT NULL,
    organization_mrn VARCHAR NOT NULL,
    endpoint_uri VARCHAR NOT NULL,
    endpoint_type VARCHAR DEFAULT 'REST',
    status VARCHAR DEFAULT 'active',
    coverage_area_wkt TEXT,
    bbox_min_lat FLOAT,
    bbox_max_lat FLOAT,
    bbox_min_lng FLOAT,
    bbox_max_lng FLOAT,
    service_metadata JSON,
    last_health_check TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- デモサービス仕様データ
INSERT INTO service_specifications (mrn, name, version, description, keywords, status, organization_mrn) VALUES
('urn:mrn:mcp:service:demo:weather', 'Weather Information Service', '1.0.0', 'Marine weather information service', '["weather", "marine", "forecast"]', 'released', 'urn:mrn:mcp:org:demo:maritime-authority'),
('urn:mrn:mcp:service:demo:vessel-tracking', 'Vessel Tracking Service', '1.0.0', 'Real-time vessel position tracking', '["tracking", "vessel", "position"]', 'released', 'urn:mrn:mcp:org:demo:maritime-authority'),
('urn:mrn:mcp:service:demo:port-info', 'Port Information Service', '1.0.0', 'Port facilities and services information', '["port", "facilities", "services"]', 'released', 'urn:mrn:mcp:org:demo:port-authority');

-- デモサービスインスタンスデータ
INSERT INTO service_instances (mrn, name, version, service_specification_mrn, organization_mrn, endpoint_uri, endpoint_type, status, coverage_area_wkt, bbox_min_lat, bbox_max_lat, bbox_min_lng, bbox_max_lng) VALUES
('urn:mrn:mcp:instance:demo:weather:001', 'Tokyo Bay Weather Service', '1.0.0', 'urn:mrn:mcp:service:demo:weather', 'urn:mrn:mcp:org:demo:maritime-authority', 'http://weather-demo.mcp.local/api', 'REST', 'active', 'POLYGON((139.5 35.4, 140.0 35.4, 140.0 35.8, 139.5 35.8, 139.5 35.4))', 35.4, 35.8, 139.5, 140.0),
('urn:mrn:mcp:instance:demo:vessel-tracking:001', 'Tokyo Bay Vessel Tracking', '1.0.0', 'urn:mrn:mcp:service:demo:vessel-tracking', 'urn:mrn:mcp:org:demo:maritime-authority', 'http://tracking-demo.mcp.local/api', 'REST', 'active', 'POLYGON((139.5 35.4, 140.0 35.4, 140.0 35.8, 139.5 35.8, 139.5 35.4))', 35.4, 35.8, 139.5, 140.0),
('urn:mrn:mcp:instance:demo:port-info:001', 'Tokyo Port Information', '1.0.0', 'urn:mrn:mcp:service:demo:port-info', 'urn:mrn:mcp:org:demo:port-authority', 'http://port-demo.mcp.local/api', 'REST', 'active', 'POINT(139.77 35.63)', 35.63, 35.63, 139.77, 139.77);