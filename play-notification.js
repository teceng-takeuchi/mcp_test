#!/usr/bin/env node

const { exec } = require('child_process');
const os = require('os');

function playNotificationSound() {
  const platform = os.platform();
  
  if (platform === 'darwin') {
    // macOS
    exec('afplay /System/Library/Sounds/Glass.aiff');
  } else if (platform === 'linux') {
    // Linux
    exec('paplay /usr/share/sounds/freedesktop/stereo/complete.oga || aplay /usr/share/sounds/sound-icons/trumpet-12.wav');
  } else if (platform === 'win32') {
    // Windows
    exec('powershell -c (New-Object Media.SoundPlayer "C:\\Windows\\Media\\notify.wav").PlaySync();');
  }
}

// メインプロセスから呼び出された場合は音を鳴らす
if (require.main === module) {
  playNotificationSound();
}

module.exports = { playNotificationSound };