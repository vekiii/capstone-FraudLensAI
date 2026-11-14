// Reproducible headless smoke: owned hidden processes, authored TEST corpus only.
import { spawn, execFileSync } from 'node:child_process';
import { mkdir, readFile, writeFile, rename, access } from 'node:fs/promises';
import { createServer } from 'node:net';
import { resolve, join } from 'node:path';
import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';
const root = process.cwd(); const work = join(root, '.cache', '003-smoke-' + randomUUID());
const report = { mode: 'automated headless Chrome; authored TEST corpus, not reviewed real corpus', checks: [], errors: [] };
const owned = []; const pause = ms => new Promise(r => setTimeout(r, ms));
let browser, tab, setup, renamed = false;
const env = { ...process.env, PYTHONPATH: join(root, 'backend/src'), INVESTIGATION_ENABLED: 'true', INVESTIGATION_PROVIDER: 'test', APP_MODE: 'fixture' };
delete env.OPENAI_API_KEY; delete env.OPENAI_MODEL;
function note(name, detail = '') { report.checks.push({ name, detail, status: 'PASS' }); }
function start(program, args) { const child = spawn(program, args, { cwd: root, env, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] }); owned.push(child); child.stdout.on('data', () => {}); child.stderr.on('data', () => {}); return child; }
function stop(child) { if (child && child.exitCode === null) execFileSync('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'], { windowsHide: true, stdio: 'ignore' }); }
async function free(port) { await new Promise((ok, no) => { const s = createServer(); s.once('error', no); s.listen(port, '127.0.0.1', () => s.close(ok)); }); }
async function ready(url) { for (let i = 0; i < 80; i++) { try { const r = await fetch(url); if (r.ok) return; } catch {} await pause(100); } throw Error('Service unavailable: ' + url); }
async function connect(url) {
  const ws = new WebSocket(url); let seq = 0; const pending = new Map(); const listeners = new Map();
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = no; });
  ws.onmessage = ({ data }) => { const message = JSON.parse(data); if (message.id) { const p = pending.get(message.id); if (p) { clearTimeout(p.timer); pending.delete(message.id); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result); } } else for (const fn of listeners.get(message.method) ?? []) fn(message.params); };
  return { ws, on(name, fn) { listeners.set(name, [...(listeners.get(name) ?? []), fn]); }, send(method, params = {}) { return new Promise((resolve, reject) => { const id = ++seq; const timer = setTimeout(() => { pending.delete(id); reject(Error('CDP timeout: ' + method)); }, 10000); pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params })); }); } };
}
try {
  for (const port of [8000, 5173, 9228]) await free(port);
  await mkdir(work, { recursive: true });
  execFileSync(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-knowledge-smoke-prepare.py', work], { env, windowsHide: true });
  setup = JSON.parse(await readFile(join(work, 'setup.json'), 'utf8')); env.INVESTIGATION_STORE = setup.store;
  let backend = start('uv', ['run', '--locked', 'uvicorn', 'fraudlens.main:app', '--app-dir', 'backend/src', '--host', '127.0.0.1', '--port', '8000']);
  start('cmd.exe', ['/c', 'npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort']);
  await ready('http://127.0.0.1:8000/api/health'); await ready('http://127.0.0.1:5173/');
  for (const base of ['http://127.0.0.1:8000', 'http://127.0.0.1:5173']) {
    const response = await fetch(base + '/api/knowledge/search?q=money'); assert.equal(response.status, 200);
    const result = await response.json(); assert.equal(result.corpus_version, setup.old); assert(result.hits.length > 0);
    assert.equal((await fetch(base + '/api/cases/CASE-999')).status, 404); assert.equal((await fetch(base + '/api/cases/CASE-1')).status, 422);
    note('Real API/proxy search, 404/422', base);
  }
  start('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=9228', '--user-data-dir=' + join(work, 'chrome-profile'), '--no-first-run', '--no-default-browser-check', 'about:blank']);
  await ready('http://127.0.0.1:9228/json/version');
  const version = await (await fetch('http://127.0.0.1:9228/json/version')).json(); report.browser = version.Browser;
  browser = await connect(version.webSocketDebuggerUrl);
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank' });
  const targets = await (await fetch('http://127.0.0.1:9228/json/list')).json(); tab = await connect(targets.find(t => t.id === targetId).webSocketDebuggerUrl);
  await tab.send('Page.enable'); await tab.send('Runtime.enable'); tab.on('Runtime.exceptionThrown', v => report.errors.push(v.exceptionDetails));
  const evaluate = async expression => { const value = await tab.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }); if (value.exceptionDetails) throw Error(JSON.stringify(value.exceptionDetails)); return value.result.value; };
  const wait = async expression => { for (let i = 0; i < 120; i++) { if (await evaluate(expression)) return; await pause(50); } throw Error('Browser timeout: ' + expression); };
  const nav = index => evaluate(`document.querySelector('[aria-label="Prikazi aplikacije"]').querySelectorAll('button')[${index}].click()`);
  const query = value => evaluate(`document.querySelector('form input').value=${JSON.stringify(value)}; document.querySelector('form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}))`);
  await tab.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3");
  for (const id of ['CASE-001', 'CASE-002', 'CASE-003']) {
    await evaluate(`document.querySelector('[aria-label="Otvori ${id}"]').click()`); await wait("!!document.querySelector('.risk-score')");
    const detail = await (await fetch('http://127.0.0.1:8000/api/cases/' + id)).json(); assert((await evaluate('document.body.innerText')).includes(detail.risk_assessment.explanation));
    await evaluate("document.querySelector('.button-back').click()"); await wait("!document.querySelector('.risk-score')");
  }
  note('Original three-case list/detail/back');
  await nav(1); await wait("document.body.innerText.includes('Unesite upit')");
  // Publish the changed authored TEST version only after UI has pinned the old one.
  execFileSync(join(root, '.venv/Scripts/python.exe'), ['-c', 'from fraudlens.investigation.knowledge import KnowledgeStore; import sys; print(KnowledgeStore(sys.argv[1]).publish(sys.argv[2]))', setup.store, setup.manifest], { env, windowsHide: true });
  const latest = await (await fetch('http://127.0.0.1:8000/api/knowledge/documents')).json(); assert.notEqual(latest.corpus_version, setup.old);
  await query('money'); await wait("!!document.querySelector('[data-passage]')");
  const oldHits = await (await fetch(`http://127.0.0.1:8000/api/knowledge/search?q=money&corpus=${setup.old}&retrieval=${setup.retrieval}`)).json();
  await evaluate("document.querySelector('[data-passage]').click()"); await wait("!!document.querySelector('pre')");
  assert.equal(await evaluate("document.querySelector('pre').textContent"), oldHits.hits[0].passage.text);
  assert((await evaluate('document.body.innerText')).includes('SIMULATED'));
  note('Exact historical source/provenance inspected after controlled corpus replacement', setup.old);
  await query('nomatchxyz'); await wait("document.body.innerText.includes('Nema dovoljno')"); note('No-match UI');
  await nav(0); await rename(setup.store, setup.store + '.offline'); renamed = true;
  await nav(1); await wait("document.body.innerText.includes('Pretraga nije spremna')"); note('Actual missing-store UI, no fabricated hits');
  await rename(setup.store + '.offline', setup.store); renamed = false;
  await evaluate("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Pokušaj')).click()"); await wait("document.body.innerText.includes('Unesite upit')");
  await query('money'); await wait("!!document.querySelector('[data-passage]')"); await evaluate("document.querySelector('[data-passage]').click()"); await wait("!!document.querySelector('pre')");
  assert((await evaluate("document.querySelector('pre').textContent")).includes('NEW')); note('Missing-store Retry recovery to new corpus');
  await nav(0); await wait("document.querySelectorAll('.case-choice').length===3");
  stop(backend); await pause(300); await evaluate("document.querySelector('.case-choice').click()"); await wait("!!document.querySelector('[role=alert]')");
  backend = start('uv', ['run', '--locked', 'uvicorn', 'fraudlens.main:app', '--app-dir', 'backend/src', '--host', '127.0.0.1', '--port', '8000']);
  await ready('http://127.0.0.1:8000/api/health');
  await evaluate("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.includes('Pokušaj')).click()"); await wait("!!document.querySelector('.risk-score')"); note('Real backend shutdown/restart original Retry');
  assert.equal(report.errors.length, 0); note('No uncaught browser exceptions'); report.status = 'PASS';
} catch (error) { report.status = 'FAIL'; report.failure = String(error.stack ?? error); process.exitCode = 1; }
finally {
  if (renamed && setup) { try { await rename(setup.store + '.offline', setup.store); } catch {} }
  try { await browser?.send('Browser.close'); } catch {} tab?.ws.close(); browser?.ws.close();
  for (const child of owned.reverse()) { try { stop(child); } catch (error) { report.cleanup_error = String(error); } }
  await writeFile('evidence/tasks/feature-003-knowledge-smoke-results.json', JSON.stringify(report, null, 2) + '\n'); console.log(JSON.stringify(report, null, 2));
}
