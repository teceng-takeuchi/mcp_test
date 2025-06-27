# Maritime Connectivity Platform (MCP) 技術仕様

## アーキテクチャ概要

MCPはサービス指向アーキテクチャ（SOA）として設計されており、マイクロサービスアプローチを採用しています。各コンポーネントは独立して開発、デプロイ、スケーリングが可能です。

```mermaid
graph TB
    subgraph "外部システム"
        V[船舶システム]
        S[拠点システム]
        E[外部サービス]
    end
    
    subgraph "MCPプラットフォーム"
        subgraph "認証・認可層"
            KC[Keycloak<br/>Identity Broker]
            MIR[Maritime Identity Registry<br/>MIR]
        end
        
        subgraph "サービス層"
            MSR[Maritime Service Registry<br/>MSR]
            MMS[Maritime Messaging Service<br/>MMS]
        end
        
        subgraph "インフラ層"
            NG[Nginx<br/>API Gateway]
            PG[(PostgreSQL<br/>Database)]
            RD[(Redis<br/>Cache/Session)]
        end
    end
    
    V <--> NG
    S <--> NG
    E <--> NG
    
    NG --> KC
    NG --> MIR
    NG --> MSR
    NG --> MMS
    
    KC <--> MIR
    MIR <--> PG
    MSR <--> PG
    MMS <--> RD
    MMS <--> PG
    
    MSR -.-> MIR
    MMS -.-> MIR
    MMS -.-> MSR
    
    classDef external fill:#e1f5fe
    classDef auth fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef infra fill:#fff3e0
    
    class V,S,E external
    class KC,MIR auth
    class MSR,MMS service
    class NG,PG,RD infra
```

## 技術スタック

### プロトコルと標準
- **認証**: OAUTH 2.0 / OpenID Connect
- **API**: RESTful API（HTTP/HTTPS）
- **API仕様**: OpenAPI (Swagger)
- **データ形式**: JSON, XML
- **地理空間データ**: Well Known Text (WKT) format

## コンポーネント別技術仕様

### 1. Maritime Identity Registry (MIR)

#### 認証メカニズム
- **標準**: OAUTH 2.0, OpenID Connect
- **証明書**: X.509証明書
- **PKI**: 公開鍵インフラストラクチャ

#### アイデンティティ管理
- MRN（Maritime Resource Name）ベースの識別
- 階層的な組織構造のサポート
- ロールベースアクセスコントロール（RBAC）

#### API仕様
```
GET /api/org/{mrn} - 組織情報の取得
POST /api/org - 新規組織の登録
PUT /api/org/{mrn} - 組織情報の更新
DELETE /api/org/{mrn} - 組織の削除
```

### 2. Maritime Service Registry (MSR)

#### データ構造（3層構造）

```mermaid
graph TD
    subgraph "MSR 3層データ構造"
        A[Service Specification Level<br/>サービス仕様レベル]
        B[Technical Design Level<br/>技術設計レベル]
        C[Instance Level<br/>インスタンスレベル]
        
        A --> B
        B --> C
    end
    
    subgraph "Service Specification Level"
        A1[論理的説明]
        A2[運用情報]
        A3[技術非依存仕様]
    end
    
    subgraph "Technical Design Level"
        B1[技術実装詳細]
        B2[プロトコル仕様]
        B3[データフォーマット]
    end
    
    subgraph "Instance Level"
        C1[実行中サービスURI]
        C2[エンドポイント情報]
        C3[サービスステータス]
    end
    
    A -.-> A1
    A -.-> A2
    A -.-> A3
    
    B -.-> B1
    B -.-> B2
    B -.-> B3
    
    C -.-> C1
    C -.-> C2
    C -.-> C3
    
    classDef spec fill:#e3f2fd
    classDef design fill:#f3e5f5
    classDef instance fill:#e8f5e8
    
    class A,A1,A2,A3 spec
    class B,B1,B2,B3 design
    class C,C1,C2,C3 instance
```

#### API仕様
```
# サービス仕様API
GET /api/serviceSpecifications - 全サービス仕様の取得
POST /api/serviceSpecifications - 新規サービス仕様の登録
GET /api/serviceSpecifications/{id} - 特定のサービス仕様の取得

# サービスインスタンスAPI
GET /api/serviceInstances - 全サービスインスタンスの取得
POST /api/serviceInstances - 新規サービスインスタンスの登録
GET /api/serviceInstances/{id} - 特定のサービスインスタンスの取得
```

#### サービス検索
- キーワード検索
- 地理的範囲検索（WKT形式）
- 組織別検索
- サービスタイプ別検索

#### API アクセス
- **プロトコル**: HTTP/HTTPS
- **認証**: MIRと連携した認証
- **APIドキュメント**: Swagger UI
- **テストベッドURL**: https://msr.maritimeconnectivity.net/swagger-ui/index.html

### 3. Maritime Messaging Service (MMS)

#### アーキテクチャ
- **メッセージブローカー**: 非同期メッセージング
- **プロトコル**: Maritime Message Transfer Protocol (MMTP)
- **標準化**: RTCM Standard 13900.0

#### 通信チャネル

```mermaid
graph TB
    subgraph "MMS 通信チャネル"
        MMS[Maritime Messaging Service]
        
        subgraph "IP通信"
            I1[インターネット<br/>TCP/IP]
            I2[VSAT]
            I3[4G/5G]
        end
        
        subgraph "非IP通信"
            N1[VDES<br/>VHF Data Exchange System]
            N2[NAVDAT]
            N3[HFデータ通信]
        end
    end
    
    subgraph "船舶側システム"
        V[船舶]
        V1[ECDIS]
        V2[通信機器]
    end
    
    subgraph "拠点側システム"
        S[拠点]
        S1[VTS]
        S2[港湾管制]
    end
    
    MMS <--> I1
    MMS <--> I2
    MMS <--> I3
    MMS <--> N1
    MMS <--> N2
    MMS <--> N3
    
    I1 <--> V
    I2 <--> V
    I3 <--> V
    N1 <--> V2
    N2 <--> V2
    N3 <--> V2
    
    I1 <--> S
    I2 <--> S
    I3 <--> S
    N1 <--> S2
    N2 <--> S2
    N3 <--> S2
    
    V --> V1
    V --> V2
    S --> S1
    S --> S2
    
    classDef ip fill:#e3f2fd
    classDef nonip fill:#fff3e0
    classDef vessel fill:#e8f5e8
    classDef shore fill:#f3e5f5
    
    class I1,I2,I3 ip
    class N1,N2,N3 nonip
    class V,V1,V2 vessel
    class S,S1,S2 shore
```

#### メッセージルーティング
- MRNベースのエンドポイントアドレッシング
- 動的ルーティング
- 複数通信パスの自動選択

#### メッセージ形式
```json
{
  "header": {
    "id": "message-uuid",
    "timestamp": "2024-01-01T00:00:00Z",
    "sender": "urn:mrn:mcp:vessel:imo:1234567",
    "receiver": "urn:mrn:mcp:org:mcc:service:vts",
    "subject": "Navigation Update"
  },
  "body": {
    "content": "Base64 encoded content",
    "contentType": "application/json",
    "encryption": "AES-256"
  }
}
```

## セキュリティ仕様

### 暗号化
- **転送時**: TLS 1.2以上
- **保存時**: AES-256暗号化
- **メッセージレベル**: エンドツーエンド暗号化

### 認証と認可
- **多要素認証**: サポート
- **トークンベース認証**: JWT (JSON Web Tokens)
- **APIキー管理**: セキュアな保管と定期的なローテーション

### 監査とログ
- 全APIアクセスのログ記録
- セキュリティイベントの監視
- コンプライアンスレポート機能

## 実装ガイドライン

### 開発環境のセットアップ
1. MCP SDKのインストール
2. 開発用証明書の取得
3. テストベッドへの接続設定

### 統合手順
1. MIRへの組織登録
2. サービス仕様のMSRへの登録
3. サービスインスタンスのデプロイ
4. MMSエンドポイントの設定

### ベストプラクティス
- APIレート制限の実装
- エラーハンドリングの適切な実装
- 接続の再試行ロジック
- キャッシュ戦略の実装

## パフォーマンス要件

### レスポンスタイム
- API応答: < 500ms（95パーセンタイル）
- メッセージ配信: < 2秒（通常条件下）

### スケーラビリティ
- 水平スケーリングのサポート
- ロードバランシング対応
- 高可用性構成

## 互換性

### サポートされるプラットフォーム
- Linux (Ubuntu 20.04+, CentOS 7+)
- Windows Server 2016+
- コンテナ環境 (Docker, Kubernetes)

### 言語別SDK
- Java
- .NET
- Python
- JavaScript/Node.js

## リファレンス

- MCP公式ドキュメント: https://docs.maritimeconnectivity.net/
- APIリファレンス: https://msr.maritimeconnectivity.net/swagger-ui/
- IALA Guidelines: G1128, G1183
- RTCM Standards: 13900.0