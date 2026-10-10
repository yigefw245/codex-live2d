import assert from 'node:assert/strict';
import fs from 'node:fs';

const profile = JSON.parse(fs.readFileSync(new URL('../model/yumi/soullink.profile.json', import.meta.url)));
let mode = 'http-error';
const audios = [];
globalThis.window = {};
globalThis.fetch = async url => {
  if (url === 'profile') return {ok: true, json: async () => profile};
  if (mode === 'http-error') return {ok: false, status: 500};
  if (mode === 'empty') return {ok: true, json: async () => ({})};
  return {ok: true, json: async () => ({audio_b64: 'UklGRg==', duration_sec: 1})};
};
globalThis.Audio = class {
  constructor(url) { this.src = url; this.duration = 1; audios.push(this); }
  play() { return mode === 'play-error' ? Promise.reject(new Error('Output unavailable')) : Promise.resolve(); }
  pause() {}
};
// Exercise the exact built bundle that the desktop loads, including SDK errors
// that resolve its speak promise instead of rejecting it.
const bundle = fs.readFileSync(new URL('../tools/web/lib/soullink-emotion.esm.js', import.meta.url));
await import('data:text/javascript;base64,' + bundle.toString('base64'));
const bridge = window.__soullink;
await bridge.start({profileUrl: 'profile', ttsUrl: 'tts', lipSyncGain: 1, headTiltGain: 1});
try {
  await assert.rejects(bridge.speak({text: 'test'}), /TTS HTTP 500/);
  assert.equal(audios.length, 0);
  mode = 'empty';
  await assert.rejects(bridge.speak({text: 'test'}), /no audio/);
  mode = 'play-error';
  await assert.rejects(bridge.speak({text: 'test'}), /Output unavailable/);
  mode = 'ok';
  let completed = false;
  const playing = bridge.speak({text: 'test'}).then(() => { completed = true; });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(completed, false, 'Must wait for actual audio completion');
  audios.at(-1).onended();
  await playing;
  assert.equal(completed, true);
  const broken = bridge.speak({text: 'test'});
  await new Promise(resolve => setImmediate(resolve));
  const rejected = assert.rejects(broken, /Audio playback failed/);
  audios.at(-1).onerror();
  await rejected;
  const cancelled = bridge.speak({text: 'test'});
  await new Promise(resolve => setImmediate(resolve));
  bridge.stopVoice();
  await cancelled;
  console.log('Built Soullink: HTTP, empty audio, playback errors, completion and cancellation passed.');
} finally {
  bridge.stop();
}
