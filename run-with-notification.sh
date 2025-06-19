#!/bin/bash

# 使い方: ./run-with-notification.sh <コマンド>
# 例: ./run-with-notification.sh npm test

# コマンドを実行
"$@"
exit_code=$?

# タスク完了時に音を鳴らす
node play-notification.js

# 元のコマンドの終了コードを返す
exit $exit_code