# Next.js 15アプリからWebSocketを使ってLokiにログを送信する実装例

この実装例では、Next.js 15アプリケーションの開発環境からconsole.logをキャプチャし、WebSocketを経由してLokiに送信する方法を示します。

## 1. 必要なパッケージのインストール

```bash
npm install --save-dev next-logger-websocket
# または
yarn add --dev next-logger-websocket
```

## 2. ロガーの設定

### `src/utils/logger.ts` ファイルの作成

```typescript
import { createWebSocketLogger } from 'next-logger-websocket';

// 環境変数に基づいてロギングを有効/無効にする
const isDevelopment = process.env.NODE_ENV === 'development';
const isClient = typeof window !== 'undefined';

// WebSocketロガーの設定
export const logger = createWebSocketLogger({
  enabled: isDevelopment, // 開発環境でのみ有効
  websocketUrl: 'ws://localhost:9023', // WebSocketサーバーのURL
  appName: 'nextjs-app', // アプリケーション名
  batchInterval: 1000, // ログをバッチ処理する間隔（ミリ秒）
  maxBatchSize: 10, // バッチあたりの最大ログ数
  labels: {
    environment: process.env.NODE_ENV || 'development',
    runtime: isClient ? 'browser' : 'server',
  },
  // エラー発生時のコールバック
  onError: (error) => {
    console.error('WebSocket logger error:', error);
  }
});

// console.logなどのメソッドをオーバーライド
if (isDevelopment) {
  const originalConsole = { ...console };
  
  // console.logのオーバーライド
  console.log = (...args) => {
    originalConsole.log(...args);
    logger.log('info', ...args);
  };
  
  // console.errorのオーバーライド
  console.error = (...args) => {
    originalConsole.error(...args);
    logger.log('error', ...args);
  };
  
  // console.warnのオーバーライド
  console.warn = (...args) => {
    originalConsole.warn(...args);
    logger.log('warn', ...args);
  };
  
  // console.infoのオーバーライド
  console.info = (...args) => {
    originalConsole.info(...args);
    logger.log('info', ...args);
  };
  
  // console.debugのオーバーライド
  console.debug = (...args) => {
    originalConsole.debug(...args);
    logger.log('debug', ...args);
  };
}

export default logger;
```

## 3. Next.jsアプリケーションへの統合

### `src/app/layout.tsx` ファイルの更新

```tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

// ロガーをインポート（クライアントサイドでのみ実行）
import dynamic from 'next/dynamic';

const LoggerInitializer = dynamic(
  () => import('@/components/LoggerInitializer'),
  { ssr: false }
);

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Next.js App with WebSocket Logger',
  description: 'Next.js app with WebSocket logger to Loki',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {process.env.NODE_ENV === 'development' && <LoggerInitializer />}
        {children}
      </body>
    </html>
  );
}
```

### `src/components/LoggerInitializer.tsx` ファイルの作成

```tsx
'use client';

import { useEffect } from 'react';
import '../utils/logger'; // ロガーを初期化

export default function LoggerInitializer() {
  useEffect(() => {
    console.log('WebSocket logger initialized');
    
    // グローバルエラーハンドラーの設定
    const originalOnError = window.onerror;
    window.onerror = (message, source, lineno, colno, error) => {
      console.error('Global error:', { message, source, lineno, colno, error });
      if (originalOnError) {
        return originalOnError(message, source, lineno, colno, error);
      }
      return false;
    };
    
    // Promiseエラーハンドラーの設定
    const originalOnUnhandledRejection = window.onunhandledrejection;
    window.onunhandledrejection = (event) => {
      console.error('Unhandled Promise rejection:', event.reason);
      if (originalOnUnhandledRejection) {
        originalOnUnhandledRejection(event);
      }
    };
    
    return () => {
      // クリーンアップ
      window.onerror = originalOnError;
      window.onunhandledrejection = originalOnUnhandledRejection;
    };
  }, []);
  
  return null; // UIは何も表示しない
}
```

## 4. `next-logger-websocket` パッケージの実装

このパッケージは存在しない架空のものですが、以下のような実装が考えられます：

### `next-logger-websocket/src/index.ts`

```typescript
interface WebSocketLoggerOptions {
  enabled: boolean;
  websocketUrl: string;
  appName: string;
  batchInterval?: number;
  maxBatchSize?: number;
  labels?: Record<string, string>;
  onError?: (error: Error) => void;
}

interface LogEntry {
  level: string;
  message: string;
  timestamp: string;
  labels: Record<string, string>;
  [key: string]: any;
}

export function createWebSocketLogger(options: WebSocketLoggerOptions) {
  if (!options.enabled) {
    // ロギングが無効の場合は何もしないロガーを返す
    return {
      log: () => {},
      connect: () => {},
      disconnect: () => {},
    };
  }

  let socket: WebSocket | null = null;
  let isConnected = false;
  let reconnectAttempts = 0;
  let reconnectTimeout: NodeJS.Timeout | null = null;
  let logQueue: LogEntry[] = [];
  let flushInterval: NodeJS.Timeout | null = null;

  const connect = () => {
    try {
      socket = new WebSocket(options.websocketUrl);

      socket.onopen = () => {
        console.log(`[WebSocketLogger] Connected to ${options.websocketUrl}`);
        isConnected = true;
        reconnectAttempts = 0;
        flushLogs();
        
        // 定期的にログをフラッシュする
        if (flushInterval) clearInterval(flushInterval);
        flushInterval = setInterval(flushLogs, options.batchInterval || 1000);
      };

      socket.onclose = () => {
        isConnected = false;
        if (flushInterval) clearInterval(flushInterval);
        
        // 再接続ロジック
        const reconnectDelay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        console.log(`[WebSocketLogger] Connection closed. Reconnecting in ${reconnectDelay}ms...`);
        
        if (reconnectTimeout) clearTimeout(reconnectTimeout);
        reconnectTimeout = setTimeout(() => {
          reconnectAttempts++;
          connect();
        }, reconnectDelay);
      };

      socket.onerror = (error) => {
        console.error('[WebSocketLogger] WebSocket error:', error);
        if (options.onError) {
          options.onError(new Error('WebSocket connection error'));
        }
      };

      socket.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          if (response.status === 'error') {
            console.error('[WebSocketLogger] Server error:', response);
          }
        } catch (error) {
          console.error('[WebSocketLogger] Failed to parse server response:', error);
        }
      };
    } catch (error) {
      console.error('[WebSocketLogger] Failed to connect:', error);
      if (options.onError) {
        options.onError(error instanceof Error ? error : new Error(String(error)));
      }
    }
  };

  const disconnect = () => {
    if (socket) {
      socket.close();
      socket = null;
    }
    if (flushInterval) {
      clearInterval(flushInterval);
      flushInterval = null;
    }
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
    isConnected = false;
  };

  const flushLogs = () => {
    if (!isConnected || !socket || logQueue.length === 0) return;

    try {
      // Lokiフォーマットに変換
      const lokiPayload = {
        streams: [
          {
            stream: {
              app: options.appName,
              ...options.labels,
            },
            values: logQueue.map(entry => [
              entry.timestamp,
              JSON.stringify({
                level: entry.level,
                message: entry.message,
                ...entry,
              })
            ])
          }
        ]
      };

      socket.send(JSON.stringify(lokiPayload));
      logQueue = [];
    } catch (error) {
      console.error('[WebSocketLogger] Failed to send logs:', error);
      if (options.onError) {
        options.onError(error instanceof Error ? error : new Error(String(error)));
      }
    }
  };

  const log = (level: string, ...args: any[]) => {
    if (!options.enabled) return;

    try {
      const message = args.map(arg => {
        if (typeof arg === 'object') {
          try {
            return JSON.stringify(arg);
          } catch (e) {
            return String(arg);
          }
        }
        return String(arg);
      }).join(' ');

      const entry: LogEntry = {
        level,
        message,
        timestamp: String(BigInt(Date.now()) * BigInt(1000000)), // ナノ秒タイムスタンプ
        labels: options.labels || {},
      };

      logQueue.push(entry);

      // キューがmaxBatchSizeを超えたらすぐにフラッシュ
      if (logQueue.length >= (options.maxBatchSize || 10)) {
        flushLogs();
      }
    } catch (error) {
      console.error('[WebSocketLogger] Failed to log:', error);
      if (options.onError) {
        options.onError(error instanceof Error ? error : new Error(String(error)));
      }
    }
  };

  // 自動接続
  connect();

  // ブラウザの場合、ページがアンロードされる前にログをフラッシュ
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      flushLogs();
    });
  }

  return {
    log,
    connect,
    disconnect,
  };
}
```

## 5. サーバーサイドのログキャプチャ

Next.jsのサーバーサイドログをキャプチャするには、カスタムサーバーを使用するか、ミドルウェアを実装します。

### `middleware.ts`

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import logger from './src/utils/logger';

// ミドルウェアでリクエスト/レスポンスをログに記録
export function middleware(request: NextRequest) {
  const start = Date.now();
  const requestId = crypto.randomUUID();
  
  // リクエスト情報をログに記録
  logger.log('info', {
    type: 'request',
    requestId,
    method: request.method,
    url: request.url,
    headers: Object.fromEntries(request.headers),
  });
  
  const response = NextResponse.next();
  
  // レスポンス情報をログに記録
  const duration = Date.now() - start;
  logger.log('info', {
    type: 'response',
    requestId,
    status: response.status,
    duration,
  });
  
  return response;
}

// 特定のパスにのみミドルウェアを適用
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 6. Grafanaでのダッシュボード設定

Grafanaでダッシュボードを設定するには、以下のようなクエリを使用します：

### ブラウザログのクエリ

```
{app="nextjs-app", runtime="browser"} | json | line_format "{{.level}}: {{.message}}"
```

### サーバーログのクエリ

```
{app="nextjs-app", runtime="server"} | json | line_format "{{.level}}: {{.message}}"
```

### エラーログのクエリ

```
{app="nextjs-app", level="error"} | json
```

### リクエスト/レスポンスのクエリ

```
{app="nextjs-app"} | json | type="request" or type="response" | line_format "{{.method}} {{.url}} {{.status}} {{.duration}}ms"
```

## 7. 本番環境での設定

本番環境では、 `next.config.js` で環境変数を設定して、ロギングを無効化できます：

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
        ENABLE_WEBSOCKET_LOGGING: process.env.NODE_ENV === 'development' ? 'true' : 'false',
    },
};

module.exports = nextConfig;
```

そして、ロガーの設定を更新します：

```typescript
export const logger = createWebSocketLogger({
  enabled: process.env.ENABLE_WEBSOCKET_LOGGING === 'true',
  // 他の設定...
});
```

これにより、本番環境ではWebSocketロギングが無効化されます。 
