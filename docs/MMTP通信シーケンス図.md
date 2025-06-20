# MMTP準拠通信シーケンス図

Maritime Message Transfer Protocol (MMTP)に準拠した完全な通信フローを図示します。

## 1. 基本メッセージ送信シーケンス

```mermaid
sequenceDiagram
    participant Vessel as 🚢 船舶
    participant MMS as 📡 MMS
    participant MSR as 🗄️ MSR
    participant MIR as 🔐 MIR
    participant Shore as 🏛️ 沿岸局

    Note over Vessel, Shore: MMTP基本通信フロー

    %% 1. 認証・接続確立
    Vessel->>MIR: 1. 身元証明書検証要求
    MIR-->>Vessel: 2. 証明書チェーン + PKI検証結果
    
    Vessel->>MMS: 3. WebSocket接続 + 証明書
    MMS->>MIR: 4. 証明書検証
    MIR-->>MMS: 5. 検証結果 (Valid/Invalid)
    MMS-->>Vessel: 6. 接続確立 (Authenticated)

    %% 2. サービス発見
    Vessel->>MSR: 7. サービス発見要求 (VTS Tokyo Bay)
    MSR-->>Vessel: 8. サービスエンドポイント情報

    %% 3. メッセージ送信
    Vessel->>MMS: 9. MMTP Message (位置報告)
    Note right of MMS: メッセージ構造:<br/>- Header (version, id, timestamp)<br/>- Security (signature, encryption)<br/>- Payload (position data)
    
    MMS->>MIR: 10. 送信者証明書検証
    MIR-->>MMS: 11. 検証結果
    
    MMS->>MSR: 12. 受信者サービス検索
    MSR-->>MMS: 13. 受信者エンドポイント

    %% 4. メッセージ配信
    MMS->>Shore: 14. MMTP Message配信
    Shore->>MIR: 15. 送信者証明書検証
    MIR-->>Shore: 16. 検証結果
    Shore-->>MMS: 17. 配信確認 (ACK)
    MMS-->>Vessel: 18. 送信完了通知
```

## 2. セキュアメッセージング（暗号化）

```mermaid
sequenceDiagram
    participant Vessel as 🚢 船舶
    participant MMS as 📡 MMS
    participant CA as 🏛️ MCP-CA
    participant Shore as 🏛️ 沿岸局

    Note over Vessel, Shore: セキュア通信 (CONFIDENTIAL Level)

    %% 鍵交換
    Vessel->>Shore: 1. 公開鍵要求
    Shore->>CA: 2. 証明書取得
    CA-->>Shore: 3. 有効な証明書
    Shore-->>Vessel: 4. 公開鍵 + 証明書

    %% メッセージ暗号化・送信
    Note over Vessel: AES-256キー生成<br/>メッセージ暗号化<br/>RSAで鍵暗号化
    
    Vessel->>MMS: 5. 暗号化MMTP Message
    Note right of MMS: 構造:<br/>- Header (平文)<br/>- Encrypted Key (RSA)<br/>- Encrypted Payload (AES)<br/>- Digital Signature

    MMS->>Shore: 6. 暗号化メッセージ配信
    
    Note over Shore: RSAで鍵復号<br/>AESでペイロード復号<br/>署名検証
    
    Shore-->>MMS: 7. 配信確認 (暗号化)
    MMS-->>Vessel: 8. 確認通知
```

## 3. 緊急メッセージ配信

```mermaid
sequenceDiagram
    participant Vessel as 🚢 船舶
    participant MMS as 📡 MMS
    participant VDES as 📻 VDES
    participant SAT as 🛰️ Inmarsat
    participant MRCC as 🆘 MRCC

    Note over Vessel, MRCC: 緊急通信 (URGENT Priority)

    %% 緊急メッセージ送信
    Vessel->>MMS: 1. URGENT Message (Distress Alert)
    Note right of MMS: Priority: URGENT<br/>Type: distress_alert<br/>Security: RESTRICTED

    %% マルチチャネル配信
    par 複数チャネル同時配信
        MMS->>VDES: 2a. VHF配信
        and
        MMS->>SAT: 2b. 衛星配信
        and
        MMS->>MRCC: 2c. 直接配信 (Internet)
    end

    %% 配信確認
    VDES-->>MMS: 3a. VHF配信確認
    SAT-->>MMS: 3b. 衛星配信確認
    MRCC-->>MMS: 3c. MRCC受信確認

    MMS-->>Vessel: 4. 全チャネル配信完了
    
    %% 緊急対応
    MRCC->>Vessel: 5. 緊急対応指示
```

## 4. Store-and-Forward機能

```mermaid
sequenceDiagram
    participant Vessel as 🚢 船舶
    participant MMS as 📡 MMS
    participant DB as 🗄️ Message Store
    participant Shore as 🏛️ 沿岸局 (オフライン)

    Note over Vessel, Shore: Store-and-Forward シナリオ

    %% メッセージ送信試行
    Vessel->>MMS: 1. MMTP Message
    MMS->>Shore: 2. 配信試行
    Note over Shore: オフライン
    
    %% ストア処理
    MMS->>DB: 3. メッセージ保存
    Note right of DB: TTL: 24時間<br/>Retry: 15分間隔<br/>Status: PENDING

    MMS-->>Vessel: 4. Store確認 (QUEUED)

    %% リトライ処理
    loop 定期リトライ
        MMS->>Shore: 5. 再配信試行
        Note over Shore: まだオフライン
    end

    %% 成功配信
    Note over Shore: オンライン復帰
    MMS->>Shore: 6. 配信成功
    Shore-->>MMS: 7. 受信確認
    
    MMS->>DB: 8. ステータス更新 (DELIVERED)
    MMS-->>Vessel: 9. 最終配信通知
```

## 5. メッセージ完全性検証

```mermaid
sequenceDiagram
    participant Sender as 📤 送信者
    participant MMS as 📡 MMS
    participant Receiver as 📥 受信者

    Note over Sender, Receiver: メッセージ完全性検証フロー

    %% メッセージ作成・署名
    Note over Sender: 1. メッセージ作成<br/>2. SHA-256ハッシュ計算<br/>3. 秘密鍵で署名
    
    Sender->>MMS: 4. 署名付きMMTP Message
    Note right of MMS: 構造:<br/>- Message Body<br/>- SHA-256 Hash<br/>- Digital Signature<br/>- Certificate

    %% MMS側検証
    Note over MMS: 5. 証明書検証<br/>6. 署名検証<br/>7. ハッシュ検証
    
    alt 検証成功
        MMS->>Receiver: 8. メッセージ転送
        
        %% 受信者側検証
        Note over Receiver: 9. 証明書チェーン検証<br/>10. 署名検証<br/>11. 完全性確認
        
        Receiver-->>MMS: 12. 受信確認 (VERIFIED)
        MMS-->>Sender: 13. 配信確認
    else 検証失敗
        MMS-->>Sender: 8. エラー通知 (VERIFICATION_FAILED)
    end
```

## 6. マルチチャネル自動切り替え

```mermaid
sequenceDiagram
    participant Vessel as 🚢 船舶
    participant MMS as 📡 MMS
    participant Internet as 🌐 Internet
    participant VDES as 📻 VDES
    participant SAT as 🛰️ Satellite
    participant Shore as 🏛️ 沿岸局

    Note over Vessel, Shore: チャネル自動切り替え

    %% 初期配信試行
    Vessel->>MMS: 1. Message (位置報告)
    MMS->>Internet: 2. Internet配信試行
    Note over Internet: ❌ 接続エラー
    
    %% 代替チャネル選択
    Note over MMS: チャネル優先度:<br/>1. Internet (失敗)<br/>2. VDES<br/>3. Satellite
    
    MMS->>VDES: 3. VDES配信試行
    VDES->>Shore: 4. VHF経由配信
    Shore-->>VDES: 5. 受信確認
    VDES-->>MMS: 6. 配信成功
    
    MMS-->>Vessel: 7. 配信完了 (via VDES)

    %% Internet復旧後
    Note over Internet: ✅ 接続復旧
    
    Vessel->>MMS: 8. 次のMessage
    MMS->>Internet: 9. Internet配信 (復旧)
    Internet->>Shore: 10. Internet経由配信
    Shore-->>Internet: 11. 受信確認
    Internet-->>MMS: 12. 配信成功
    MMS-->>Vessel: 13. 配信完了 (via Internet)
```

## メッセージ構造詳細

### MMTPヘッダー構造
```yaml
header:
  version: "1.0"
  message_id: "uuid-v4"
  correlation_id: "optional"
  timestamp: "ISO-8601"
  ttl: 86400  # seconds
  priority: "NORMAL|HIGH|URGENT"
  security_level: "PUBLIC|RESTRICTED|CONFIDENTIAL|SECRET"
  
sender:
  mrn: "urn:mrn:mcp:vessel:imo:1234567"
  certificate: "X.509 Certificate"
  
recipient:
  mrn: "urn:mrn:mcp:shore:authority:vts:tokyo-bay"
  
payload:
  message_type: "position_report"
  subject: "位置報告"
  body: "緯度: 35.6762, 経度: 139.6503..."
  metadata: {}
  
security:
  digital_signature: "base64-encoded"
  encryption_algorithm: "AES-256-GCM"
  encrypted_key: "RSA-encrypted AES key"
```

## 実装での考慮点

1. **証明書検証**: すべてのメッセージで送信者証明書を検証
2. **暗号化**: CONFIDENTIAL以上のセキュリティレベルで必須
3. **配信保証**: TTL内での配信確認とリトライ機構
4. **チャネル冗長性**: 複数通信チャネルでの自動フェイルオーバー
5. **監査ログ**: すべての通信を改ざん防止ログに記録

このMMTP準拠実装により、商用レベルの海事通信システムが構築できます。