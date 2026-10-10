const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function element() {
  const classes = new Set();
  return {
    classList: {
      add: name => classes.add(name),
      remove: name => classes.delete(name),
      contains: name => classes.has(name),
      toggle(name, on) { on ? classes.add(name) : classes.delete(name); }
    },
    style: {}, listeners: {}, attributes: {},
    addEventListener(name, callback) { this.listeners[name] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; }
  };
}
const elements = new Map();
const context = {
  document: {getElementById(id) {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  }},
  window: {}, console, setTimeout: () => 1, clearTimeout() {},
  URLSearchParams, location: {search: ''},
};
vm.createContext(context);
const source = fs.readFileSync(path.join(__dirname, '../tools/web/live.js'), 'utf8');
vm.runInContext(source.slice(0, source.lastIndexOf('\ninit().catch')), context);
const mic = elements.get('chat-mic');
const bubble = elements.get('bubble');
context.window.notify('recording started', 4000);
assert.equal(bubble.textContent, 'recording started');
assert.equal(bubble.classList.contains('show'), true);
context.window.setVoiceBusy(true, 'starting');
assert.equal(mic.disabled, true);
assert.equal(mic.attributes['aria-busy'], 'true');
context.window.setVoiceBusy(false);
context.window.setVoiceRecording(true);
assert.equal(mic.disabled, false);
assert.equal(mic.classList.contains('recording'), true);
let toggled = false;
context.window.__bridge = {voice_toggle() { toggled = true; }};
mic.listeners.click();
assert.equal(toggled, true);
context.window.setVoiceInputEnabled(false);
assert.equal(mic.classList.contains('recording'), false);
assert.equal(mic.disabled, false);
const stop = elements.get('chat-stop');
context.window.setDialogueBusy(true);
assert.equal(stop.disabled, false);
let interrupted = false;
context.window.__bridge.stop_reply = () => { interrupted = true; };
stop.listeners.click();
assert.equal(interrupted, true);
context.window.setDialogueBusy(false);
assert.equal(stop.disabled, true);

async function checkSpeech() {
  const spoken = [], releases = [];
  let stopped = 0, completed = 0;
  context.speechBridge = {
    speak(payload) {
      spoken.push(payload.text);
      return new Promise(resolve => releases.push(resolve));
    },
    stopVoice() { stopped += 1; }
  };
  context.window.__bridge.tts_played = () => { completed += 1; };
  vm.runInContext('soullink.enabled = true; soullink.bridge = speechBridge;', context);
  const tick = () => new Promise(resolve => setImmediate(resolve));
  context.window.soullinkSpeak('first', 0);
  context.window.soullinkSpeak('stale queued', 0);
  context.window.finishSpeech(0);
  await tick();
  assert.deepEqual(spoken, ['first']);
  assert.equal(completed, 0);
  context.window.stopSpeech(1);
  assert.equal(stopped, 1);
  context.window.soullinkSpeak('stale late callback', 0);
  context.window.soullinkSpeak('new first', 1);
  context.window.soullinkSpeak('new last', 1);
  context.window.finishSpeech(1);
  await tick();
  assert.deepEqual(spoken, ['first', 'new first']);
  releases[0]();
  await tick();
  assert.equal(completed, 0);
  assert.deepEqual(spoken, ['first', 'new first']);
  releases[1]();
  await tick();
  assert.deepEqual(spoken, ['first', 'new first', 'new last']);
  assert.equal(completed, 0);
  releases[2]();
  await tick();
  assert.equal(completed, 1);
  const results = [];
  context.window.__bridge.tts_result = (generation, error) => results.push({generation, error});
  context.speechBridge.speak = () => Promise.reject(new Error('TTS unavailable'));
  context.window.soullinkSpeak('failed speech', 1);
  context.window.finishSpeech(1);
  await tick();
  assert.deepEqual(results, [{generation: 1, error: 'TTS unavailable'}]);
  assert.equal(completed, 1, 'Failed speech must not be reported as played');
  context.window.finishSpeech(1);
  await tick();
  assert.equal(results[1].error, 'No speech was queued');
  vm.runInContext('soullink.enabled = false;', context);
  context.window.soullinkChat({reply: 'not ready', generation: 1});
  context.window.finishSpeech(1);
  await tick();
  assert.equal(results[2].error, 'Speech service is not ready');
  vm.runInContext('soullink.enabled = true;', context);
  context.speechBridge.speak = () => Promise.resolve();
  context.window.soullinkSpeak('recovered', 1);
  context.window.finishSpeech(1);
  await tick();
  assert.equal(results[3].error, '', 'An earlier error must not poison new speech');
}
checkSpeech().then(() => console.log('Voice UI, stop control, speech FIFO, cancellation and completion barrier passed.'))
  .catch(error => { console.error(error); process.exitCode = 1; });
