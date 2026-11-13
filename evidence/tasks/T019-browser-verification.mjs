// Run with local backend/Vite and isolated Chrome --headless --remote-debugging-port=9227.
// No added dependencies, personal browser profile or production changes.
import { writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const base = 'http://127.0.0.1:5173';
const report = { date: new Date().toISOString(), mode: 'headless Chrome via CDP', checks: [], errors: [], console: [], injected: [] };
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function connect(url) {
  const ws = new WebSocket(url); let seq = 0; const pending = new Map(); const listeners = new Map();
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
  ws.onmessage = ({ data }) => {
    const message = JSON.parse(data);
    if (message.id) { const entry = pending.get(message.id); if (entry) { clearTimeout(entry.timer); pending.delete(message.id); message.error ? entry.reject(new Error(JSON.stringify(message.error))) : entry.resolve(message.result); } }
    else for (const fn of listeners.get(message.method) ?? []) Promise.resolve(fn(message.params)).catch(error => report.errors.push(String(error)));
  };
  return { ws, on(name, fn) { listeners.set(name, [...(listeners.get(name) ?? []), fn]); },
    send(method, params = {}) { return new Promise((resolve, reject) => { const id = ++seq; const timer = setTimeout(() => { pending.delete(id); reject(new Error(`Timeout: ${method}`)); }, 12000); pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params })); }); } };
}
const version = await (await fetch('http://127.0.0.1:9227/json/version')).json();
report.browser = version.Browser;
const browser = await connect(version.webSocketDebuggerUrl);
let tab;
try {
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank' });
  const targets = await (await fetch('http://127.0.0.1:9227/json/list')).json();
  tab = await connect(targets.find(item => item.id === targetId).webSocketDebuggerUrl);
  await tab.send('Page.enable'); await tab.send('Runtime.enable');
  tab.on('Runtime.exceptionThrown', value => report.errors.push(value.exceptionDetails));
  tab.on('Runtime.consoleAPICalled', value => report.console.push({ type: value.type, args: value.args.map(arg => arg.value ?? arg.description) }));
  const evaluate = async expression => {
    const result = await tab.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  const wait = async expression => { for (let i = 0; i < 100; i++) { if (await evaluate(expression)) return; await delay(50); } throw new Error(`Condition timeout: ${expression}`); };
  const text = () => evaluate('document.body.innerText');
  const click = async selector => { assert(await evaluate(`!!document.querySelector(${JSON.stringify(selector)})`), selector); await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`); };
  const note = (name, details = '') => report.checks.push({ name, status: 'PASS', details });
  let fault = 'none';
  await tab.send('Fetch.enable', { patterns: [{ urlPattern: `${base}/api/*`, requestStage: 'Request' }] });
  tab.on('Fetch.requestPaused', async event => {
    const path = new URL(event.request.url).pathname;
    if (fault === 'outage' && path.startsWith('/api/')) { report.injected.push({ fault, path }); await tab.send('Fetch.failRequest', { requestId: event.requestId, errorReason: 'ConnectionRefused' }); return; }
    let body; let status = 200;
    if (fault === 'empty' && path === '/api/cases') body = { items: [] };
    if (fault === 'unknown' && path === '/api/cases') body = { items: [{ case_id: 'CASE-999', transaction_id: 'TX-001', score: 0.5, score_source: 'fixture' }] };
    if (fault === 'malformed' && path === '/api/cases/CASE-001') { status = 422; body = { error: { code: 'invalid_request', message: 'Invalid request.' } }; }
    if (fault === 'slow' && path === '/api/cases/CASE-001') await delay(600);
    if (body) { report.injected.push({ fault, path, status }); await tab.send('Fetch.fulfillRequest', { requestId: event.requestId, responseCode: status, responseHeaders: [{ name: 'Content-Type', value: 'application/json' }], body: Buffer.from(JSON.stringify(body)).toString('base64') }); }
    else await tab.send('Fetch.continueRequest', { requestId: event.requestId }).catch(error => { if (fault !== 'slow') throw error; });
  });
  async function load() { await tab.send('Page.navigate', { url: base }); await wait(`document.querySelectorAll('.case-choice').length > 0 || !!document.querySelector('[role="alert"]') || document.body.innerText.includes('Lista je prazna')`); }
  await tab.send('Emulation.setDeviceMetricsOverride', { width: 1365, height: 900, deviceScaleFactor: 1, mobile: false });
  await load(); note('01 Open real application');
  assert.equal(await evaluate("document.querySelectorAll('.case-choice').length"), 3); note('02 Exactly three cases');
  for (let i = 1; i <= 3; i++) {
    const id = `CASE-00${i}`;
    await click(`[aria-label="Otvori ${id}"]`);
    await wait(`!!document.querySelector('.risk-score') && document.querySelector('#panel-title').textContent === 'Slučaj ${id}'`);
    note(i === 1 ? '03 Open case 1' : i === 2 ? '06 Open case 2' : '08 Open case 3');
    const detail = await (await fetch(`${base}/api/cases/${id}`)).json();
    const shown = await text();
    for (const value of [detail.transaction.transaction_id, detail.transaction.amount, detail.transaction.currency, detail.risk_assessment.explanation, 'fixture-v1']) assert(shown.includes(value), `Missing ${value}`);
    note(i === 1 ? '04 Case 1 data/assessment' : i === 2 ? '07 Case 2 details' : '09 Case 3 details');
    await click('.button-back'); await wait("document.querySelector('#panel-title')?.textContent === 'Pregled slučajeva'");
    if (i === 1) note('05 Return to list');
  }
  assert((await text()).includes('Demonstracioni podaci — sintetički skor, bez ML predikcije')); note('10 Synthetic notice');
  await writeFile('evidence/tasks/T019-desktop.png', Buffer.from((await tab.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
  fault = 'unknown'; await load(); await click('[aria-label="Otvori CASE-999"]'); await wait("document.body.innerText.includes('CASE-999 nije pronađen')"); note('11 Unknown case', 'Injected valid list entry CASE-999; detail hits real backend 404.');
  fault = 'none'; const malformed = await evaluate("fetch('/api/cases/CASE-1').then(async r=>({status:r.status,body:await r.json()}))"); assert.equal(malformed.status, 422);
  fault = 'malformed'; await load(); await click('[aria-label="Otvori CASE-001"]'); await wait("!!document.querySelector('[role=alert]')"); note('12 Malformed ID/error handling', 'Real browser fetch CASE-1=422; injected 422 on selectable detail exercises UI controlled error.');
  fault = 'outage'; await tab.send('Page.navigate', { url: base }); await wait("!!document.querySelector('[role=alert]')");
  fault = 'none'; await click('.case-panel button'); await wait("document.querySelectorAll('.case-choice').length === 3"); note('13 Unavailable service and real Retry click', 'CDP ConnectionRefused fault injection, then restored real backend requests.');
  fault = 'empty'; await tab.send('Page.navigate', { url: base }); await wait("document.body.innerText.includes('Lista je prazna')"); note('14 Empty list', 'Injected items:[], actual Chrome rendering.');
  fault = 'none'; await click('.case-panel button'); await wait("document.querySelectorAll('.case-choice').length === 3");
  fault = 'slow'; await click('[aria-label="Otvori CASE-001"]'); await delay(70); await click('[aria-label="Otvori CASE-002"]');
  await wait("document.querySelector('#panel-title')?.textContent === 'Slučaj CASE-002' && !!document.querySelector('.risk-score')"); await delay(850);
  assert.equal(await evaluate("document.querySelector('#panel-title').textContent"), 'Slučaj CASE-002'); assert((await text()).includes('TX-002')); note('15 Rapid switching', 'Delayed CASE-001 request; CASE-002 remains selected after old request completion/cancellation.');
  fault = 'none'; await click('.button-back');
  await evaluate("document.querySelector('[aria-label=\"Otvori CASE-001\"]').focus()");
  await tab.send('Emulation.setFocusEmulationEnabled', { enabled: true });
  await tab.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', text: '\r', unmodifiedText: '\r', windowsVirtualKeyCode: 13 }); await tab.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 });
  await wait("document.querySelector('#panel-title')?.textContent === 'Slučaj CASE-001' && !!document.querySelector('.risk-score')"); note('Keyboard Enter activation', 'Actual Chrome key dispatch after focusing case button; not human keyboard review.');
  await tab.send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  assert(await evaluate('document.documentElement.scrollWidth <= innerWidth')); note('Mobile layout bounds', '390px viewport; no horizontal document overflow.');
  await writeFile('evidence/tasks/T019-mobile.png', Buffer.from((await tab.send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
  assert.equal(report.errors.length, 0); assert.equal(report.console.filter(item => item.type === 'error').length, 0); note('16 Browser console/exceptions', 'No uncaught Runtime exceptions or console.error calls. Intentional network 404/422/connection faults are expected and are not JavaScript exceptions.');
  report.status = 'PASS';
} catch (error) { report.status = 'FAIL'; report.failure = String(error.stack ?? error); process.exitCode = 1; }
finally {
  await writeFile('evidence/tasks/T019-browser-results.json', JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  try { await browser.send('Browser.close'); } catch { /* Chrome may close before acknowledgement. */ }
  tab?.ws.close(); browser.ws.close();
}
