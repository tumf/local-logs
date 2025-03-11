# Next.js 15アプリからWebSocketを使ってLokiにログを送信する方法

Next.js 15の開発環境で出力されるconsole.logをWebSocketを経由してLokiに送信し、Grafanaでモニタリングするシステムを構築したいと思います。以下の要件を満たすソリューションを提案してください：

## 要件

1. Next.js 15アプリの開発環境（`next dev`）で出力されるconsole.logをキャプチャする
2. キャプチャしたログをWebSocketを使ってLokiに送信する
3. Grafanaでログを可視化できるようにする
4. 開発環境でのみ動作し、本番環境では無効化できること
5. TypeScriptをサポートすること

## 技術スタック

- Next.js 15
- TypeScript
- Loki（ログ集約）
- Grafana（ログ可視化）
- WebSocket（ログ転送）

## 実装のヒント

1. console.logをオーバーライドして、標準の出力と同時にWebSocketにも送信する方法
2. Next.jsのミドルウェアやプラグインを使用する方法
3. ブラウザとサーバーの両方のログをキャプチャする方法
4. 開発環境と本番環境を区別する方法
5. エラーハンドリングとフォールバックの実装方法

## 期待する成果物

1. Next.jsアプリケーションにインテグレーションするためのコード
2. WebSocketサーバーの実装またはLokiへの接続方法
3. 設定方法の詳細な説明
4. Grafanaでのダッシュボード設定例

## 追加情報

- Lokiサーバーは `http://localhost:9022/loki/api/v1/push` でアクセス可能
- WebSocketサーバーは `ws://localhost:9023` または `ws://localhost:9020/ws/` でアクセス可能
- ログフォーマットはLokiの標準フォーマットに準拠すること

```json
{
  "streams": [
    {
      "stream": {
        "app": "nextjs",
        "environment": "development",
        "level": "info"
      },
      "values": [
        ["1609455600000000000", "ログメッセージ"]
      ]
    }
  ]
}
```

よろしくお願いします。 
