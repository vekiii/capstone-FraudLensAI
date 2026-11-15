// Phase 5 actual browser/proxy/API/CLI recovery. Test provider only.
import { spawn, execFileSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { resolve, join, relative } from 'node:path';
import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';
const root = process.cwd(); const work = join(root, '.cache', '003-recovery-browser-' + randomUUID());
assert(process.argv.slice(2).every(arg => arg === '--reviewed'));
const report = { mode: 'Phase 5 automated Chrome/API/proxy/recovery CLI; authored fixture/test provider; no LLM quality claim', work, checks: [], errors: [], requests: [] };
const owned = []; const pause = ms => new Promise(r => setTimeout(r, ms));
let browser, tab, setup;
const env = { ...process.env, PYTHONPATH: join(root, 'backend/src'), INVESTIGATION_ENABLED: 'true', INVESTIGATION_PROVIDER: 'test', APP_MODE: 'fixture' };
delete env.OPENAI_API_KEY; delete env.OPENAI_MODEL;
function note(name, detail = '') { report.checks.push({ name, detail, status: 'PASS' }); }
function start(program, args) { const child = spawn(program, args, { cwd: root, env, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] }); owned.push(child); child.stdout.on('data', () => {}); child.stderr.on('data', data => { if (program.endsWith('chrome.exe')) report.chrome_stderr = ((report.chrome_stderr ?? '') + data).slice(-8000); }); return child; }
function stop(child) {
  if (!child || child.exitCode !== null) return;
  try { process.kill(child.pid, 0); } catch (error) { if (error.code === 'ESRCH') return; throw error; }
  try { execFileSync('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' }); }
  catch (error) { try { process.kill(child.pid, 0); } catch (gone) { if (gone.code === 'ESRCH') return; } throw error; }
}
function startBackend() { return start(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-recovery-runtime.py', work, 'api']); }
async function free(port) { await new Promise((ok, no) => { const s = createServer(); s.once('error', no); s.listen(port, '127.0.0.1', () => s.close(ok)); }); }
async function ready(url) { for (let i = 0; i < 80; i++) { try { const r = await fetch(url); if (r.ok) return; } catch {} await pause(100); } throw Error('Service unavailable: ' + url); }
async function connect(url) {
  const ws = new WebSocket(url); let seq = 0; const pending = new Map(); const listeners = new Map();
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = event => no(event.error ?? Error('WebSocket connection failed: ' + url)); });
  ws.onmessage = ({ data }) => { const message = JSON.parse(data); if (message.id) { const p = pending.get(message.id); if (p) { clearTimeout(p.timer); pending.delete(message.id); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result); } } else for (const fn of listeners.get(message.method) ?? []) fn(message.params); };
  return { ws, on(name, fn) { listeners.set(name, [...(listeners.get(name) ?? []), fn]); }, send(method, params = {}) { return new Promise((resolve, reject) => { const id = ++seq; const timer = setTimeout(() => { pending.delete(id); reject(Error('CDP timeout: ' + method)); }, 10000); pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params })); }); } };
}

const helper = 'evidence/tasks/feature-003-recovery-runtime.py';
const worker = () => JSON.parse(execFileSync(join(root, '.venv/Scripts/python.exe'), [helper, work, 'worker'], { env, windowsHide: true, encoding: 'utf8' }).trim());
try {
  for (const port of [8000, 5173, 9228]) await free(port);
  await mkdir(work, { recursive: true });
  execFileSync(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-knowledge-smoke-prepare.py', work], { env, windowsHide: true });
  setup = JSON.parse(await readFile(join(work, 'setup.json'), 'utf8')); env.INVESTIGATION_STORE = setup.store;
  let backend = startBackend();
  start(process.execPath, ['frontend/node_modules/vite/bin/vite.js', 'frontend', '--config', 'frontend/vite.config.ts', '--host', '127.0.0.1', '--port', '5173', '--strictPort']);
  await ready('http://127.0.0.1:8000/api/health'); await ready('http://127.0.0.1:5173/');
  start('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', '--disable-gpu', '--disable-extensions', '--disable-background-networking', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=9228', '--user-data-dir=' + join(work, 'chrome-profile'), '--no-first-run', '--no-default-browser-check', 'about:blank']);
  await ready('http://127.0.0.1:9228/json/version');
  const version = await (await fetch('http://127.0.0.1:9228/json/version')).json(); report.browser = version.Browser;
  browser = await connect(version.webSocketDebuggerUrl);
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank' });
  const targets = await (await fetch('http://127.0.0.1:9228/json/list')).json(); tab = await connect(targets.find(t => t.id === targetId).webSocketDebuggerUrl);
  await tab.send('Page.enable'); await tab.send('Runtime.enable'); tab.on('Runtime.exceptionThrown', v => report.errors.push(v.exceptionDetails));
  await tab.send('Network.enable'); tab.on('Network.responseReceived', v => { if (v.response.url.includes('/api/investigation/')) report.requests.push({ url: v.response.url, status: v.response.status }); });
  const evaluate = async expression => { const v = await tab.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }); if (v.exceptionDetails) throw Error(JSON.stringify(v.exceptionDetails)); return v.result.value; };
  const wait = async expression => { for (let i = 0; i < 160; i++) { if (await evaluate(expression)) return; await pause(50); } throw Error('Browser timeout: ' + expression); };
  const click = selector => evaluate('document.querySelector(' + JSON.stringify(selector) + ').click()');
  const openCase = async id => { await click('[aria-label="Otvori ' + id + '"]'); await wait("!!document.querySelector('[data-investigation-open]')"); await click('[data-investigation-open]'); await wait("!!document.querySelector('[data-run-state]') || !!document.querySelector('[data-start]:not(:disabled)')"); };
  const back = async () => { await click('.button-back'); await wait("!document.querySelector('.risk-score')"); };
  const get = async path => { const response = await fetch('http://127.0.0.1:8000' + path); assert.equal(response.status, 200); return response.json(); };
  const attempts = () => get('/api/investigation/runs?case_id=CASE-001');
  const path = run => '/api/investigation/attempts/' + run.attempt_id;
  const startRun = async () => { await click('[data-start]'); await wait("!!document.querySelector('[data-run-state=created]')"); return (await attempts()).items[0]; };
  await tab.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3");
  await openCase('CASE-001'); const queued = await startRun();
  await back(); await openCase('CASE-002'); assert(!(await evaluate('document.body.innerText')).includes(queued.context_revision));
  await back(); await openCase('CASE-001'); await wait("!!document.querySelector('[data-run-state=created]')");
  assert.equal((await get(path(queued))).budget.provider_requests, 0);
  note('Queued navigation and reopen preserve correct case/context with zero spend', queued.attempt_id);
  await click('[data-cancel]'); await wait("!!document.querySelector('[data-run-state=cancelled]')");
  const cancelled = await get(path(queued)); assert.equal(cancelled.state, 'cancelled'); assert.equal(cancelled.budget.provider_requests, 0);
  assert((await evaluate('document.body.innerText')).includes('dodatnu potrošnju'));
  note('Explicit browser cancel via same-origin proxy, persisted ETag/CAS state');
  // Delay an already accepted mutation response while refresh selects its saved child.
  await evaluate(`window.savedFetch = window.fetch; window.fetch = async (...args) => { const response = await window.savedFetch(...args); if (String(args[0]).endsWith('/retry')) { window.retryAccepted = true; await new Promise(resolve => { window.releaseRecovery = resolve; }); } return response; };`);
  await click('[data-retry]'); await wait('window.retryAccepted === true');
  await click('[data-refresh]'); await wait("!!document.querySelector('[data-run-state=created]')");
  const child = (await attempts()).items[0]; assert.equal(child.parent_attempt_id, cancelled.attempt_id);
  await evaluate('window.releaseRecovery(); window.fetch = window.savedFetch;'); await pause(150);
  assert.equal(worker().state, 'ready_for_review'); await wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  const saved = await get(path(child)); assert.equal(saved.budget.provider_requests, 4);
  note('Explicit child retry, read refresh during delayed reply and bounded worker completion', { parent: cancelled.attempt_id, child: child.attempt_id });
  // Kill an actual CLI process after one completed tool and a second pending dispatch.
  const interrupted = await startRun();
  const fault = start(join(root, '.venv/Scripts/python.exe'), [helper, work, 'fault-worker', 'evidence']);
  for (let i = 0; i < 140; i++) { try { await readFile(join(work, 'fault-marker.json')); break; } catch { await pause(50); } }
  const marker = JSON.parse(await readFile(join(work, 'fault-marker.json'), 'utf8'));
  assert(Number.isInteger(marker.pid) && marker.boundary === 'evidence'); // venv launcher and Python may have different PIDs
  stop(fault); await wait("!!document.querySelector('[data-run-state=failed]')");
  const failed = await get(path(interrupted)); assert.equal(failed.failure.code, 'interrupted'); assert.equal(failed.failure.outcome_unknown, true); assert.equal(failed.budget.provider_requests, 2);
  assert((await evaluate('document.body.innerText')).includes('ishod prethodnog zahteva nepoznat'));
  await back(); await openCase('CASE-002'); await back(); await openCase('CASE-001'); await wait("!!document.querySelector('[data-run-state=failed]')");
  await click('[data-retry]'); await wait("!!document.querySelector('[data-run-state=created]')");
  const recovered = (await attempts()).items[0]; assert.equal(recovered.parent_attempt_id, failed.attempt_id);
  assert.equal(worker().state, 'ready_for_review'); await wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  const done = await get(path(recovered)); assert.equal(done.budget.provider_requests, 4);
  assert.equal((await get(path(failed))).budget.provider_requests, 2);
  note('Actual killed worker, failed navigation/reopen and explicit retry preserve old counters and bound evidence', { parent: failed.attempt_id, child: done.attempt_id, old_requests: 2, new_requests: 4 });
  await click('[data-parent]'); await wait("!!document.querySelector('[data-run-state=failed]')");
  assert((await evaluate('document.body.innerText')).includes('Istorijski'));
  await click('[data-refresh]'); await wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  note('Child reopens its saved parent through a read-only action, then refresh restores latest attempt');
  // Change only the isolated context metadata, keeping repository fixtures untouched.
  const metadata = JSON.parse(await readFile(join(root, 'data/fixtures/investigation/contexts.json'), 'utf8'));
  metadata.observed_at = '2026-11-15T12:00:00Z'; await writeFile(join(work, 'metadata.json'), JSON.stringify(metadata));
  stop(backend); await pause(250); backend = startBackend(); await ready('http://127.0.0.1:8000/api/health');
  const stale = await fetch('http://127.0.0.1:8000/api/investigation/runs?case_id=CASE-001&context_revision=' + done.context_revision);
  assert.equal(stale.status, 409); assert.equal((await stale.json()).error.code, 'stale_snapshot');
  const staleRetry = await fetch('http://127.0.0.1:8000' + path(failed) + '/retry', { method: 'POST', headers: { 'Content-Type': 'application/json', 'If-Match': String((await get(path(failed))).revision), 'Idempotency-Key': randomUUID() }, body: JSON.stringify({ reuse_evidence: true }) });
  assert.equal(staleRetry.status, 409); assert.equal((await staleRetry.json()).error.code, 'stale_snapshot');
  await click('[data-refresh]'); await wait("!!document.querySelector('[data-history]')");
  const current = await attempts(); assert.equal(current.items.length, 0);
  await click('[data-history="' + done.attempt_id + '"]'); await wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  assert((await evaluate('document.body.innerText')).includes('Istorijski'));
  const citation = done.report.draft.citations[0]; await click('[data-evidence="' + citation + '"]');
  const exact = await get(path(done) + '/evidence/' + citation); await wait('Array.from(document.querySelectorAll("pre")).some(p=>p.textContent===' + JSON.stringify(exact.text) + ')');
  assert.equal((await get(path(done))).report.report_id, done.report.report_id);
  const fresh = await startRun(); assert.notEqual(fresh.context_revision, done.context_revision); assert.equal(fresh.case_id, done.case_id);
  note('Controlled same-case snapshot switch: stale reads/retries 409, historical report/citation preserved, new context distinct', { old_context: done.context_revision, new_context: fresh.context_revision });
  await click('[data-cancel]'); await wait("!!document.querySelector('[data-run-state=cancelled]')");
  // Original case UI still operates with investigation disabled and no provider configuration.
  stop(backend); await pause(250); env.INVESTIGATION_ENABLED = 'false'; backend = startBackend(); await ready('http://127.0.0.1:8000/api/health');
  await tab.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3");
  for (const id of ['CASE-001', 'CASE-002', 'CASE-003']) { await click('[aria-label="Otvori ' + id + '"]'); await wait("!!document.querySelector('.risk-score')"); assert.equal(await evaluate("document.querySelectorAll('[role=alert]').length"), 0); await back(); }
  for (const base of ['http://127.0.0.1:8000', 'http://127.0.0.1:5173']) { assert.equal((await fetch(base + '/api/cases/CASE-999')).status, 404); assert.equal((await fetch(base + '/api/cases/CASE-1')).status, 422); }
  note('Original fixture three-case list/detail/back and API/proxy 404/422 with feature disabled');
  assert.equal(report.errors.length, 0); note('No uncaught browser exceptions'); report.status = 'PASS';
} catch (error) { report.status = 'FAIL'; report.failure = String(error.stack ?? error); try { report.last_ui = (await tab.send('Runtime.evaluate', { expression: 'document.body.innerText', returnByValue: true })).result.value; } catch {} process.exitCode = 1; }
finally {
  try { await browser?.send('Browser.close'); } catch {} tab?.ws.close(); browser?.ws.close();
  for (const child of owned.reverse()) { try { stop(child); } catch (error) { report.cleanup_error = String(error); } }
  try { await pause(500); for (const port of [8000, 5173, 9228]) await free(port); report.owned_process_cleanup = 'PASS'; } catch (error) { report.cleanup_error = String(error); }
  if (report.cleanup_error) { report.status = 'FAIL'; process.exitCode = 1; }
  await writeFile('evidence/tasks/feature-003-t057-recovery-browser-results.json', JSON.stringify(report, null, 2) + '\n'); console.log(JSON.stringify(report, null, 2));
  process.exit(process.exitCode ?? 0);
}

