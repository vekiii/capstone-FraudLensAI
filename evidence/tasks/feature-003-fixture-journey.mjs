// Phase 4 browser/API/proxy/worker journey. Test provider only.
import { spawn, execFileSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { resolve, join, relative } from 'node:path';
import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';
const root = process.cwd(); const work = join(root, '.cache', '003-smoke-' + randomUUID());
assert(process.argv.slice(2).every(arg => arg === '--reviewed'));
const report = { mode: 'Phase 4 automated headless Chrome/API/proxy/worker; reviewed corpus; authored TEST provider, no live quality claim', work, checks: [], errors: [], requests: [] };
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
function startBackend() { return start(join(root, '.venv/Scripts/python.exe'), ['-m', 'uvicorn', 'fraudlens.main:app', '--app-dir', 'backend/src', '--host', '127.0.0.1', '--port', '8000']); }
async function free(port) { await new Promise((ok, no) => { const s = createServer(); s.once('error', no); s.listen(port, '127.0.0.1', () => s.close(ok)); }); }
async function ready(url) { for (let i = 0; i < 80; i++) { try { const r = await fetch(url); if (r.ok) return; } catch {} await pause(100); } throw Error('Service unavailable: ' + url); }
async function connect(url) {
  const ws = new WebSocket(url); let seq = 0; const pending = new Map(); const listeners = new Map();
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = event => no(event.error ?? Error('WebSocket connection failed: ' + url)); });
  ws.onmessage = ({ data }) => { const message = JSON.parse(data); if (message.id) { const p = pending.get(message.id); if (p) { clearTimeout(p.timer); pending.delete(message.id); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result); } } else for (const fn of listeners.get(message.method) ?? []) fn(message.params); };
  return { ws, on(name, fn) { listeners.set(name, [...(listeners.get(name) ?? []), fn]); }, send(method, params = {}) { return new Promise((resolve, reject) => { const id = ++seq; const timer = setTimeout(() => { pending.delete(id); reject(Error('CDP timeout: ' + method)); }, 10000); pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params })); }); } };
}

env.INVESTIGATION_TEST_SCENARIO = 'grounded';
const worker = () => JSON.parse(execFileSync(join(root, '.venv/Scripts/python.exe'),
  ['-m', 'fraudlens.investigation.cli', 'worker', '--store', setup.store, '--once'],
  { env, windowsHide: true, encoding: 'utf8' }).trim());
try {
  for (const port of [8000, 5173, 9228]) await free(port);
  await mkdir(work, { recursive: true });
  execFileSync(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-knowledge-smoke-prepare.py', work, '--reviewed'], { env, windowsHide: true });
  setup = JSON.parse(await readFile(join(work, 'setup.json'), 'utf8')); env.INVESTIGATION_STORE = setup.store;
  assert(!relative(work, resolve(setup.store)).startsWith('..'));
  report.corpus_version = setup.old; report.retrieval_version = setup.retrieval;
  let backend = startBackend();
  start('cmd.exe', ['/c', 'npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort']);
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
  const wait = async expression => { for (let i = 0; i < 140; i++) { if (await evaluate(expression)) return; await pause(50); } throw Error('Browser timeout: ' + expression); };
  const reload = async () => {
    let loaded; const event = new Promise(resolve => { loaded = resolve; });
    tab.on('Page.loadEventFired', () => loaded());
    await tab.send('Page.reload');
    await Promise.race([event, pause(5000).then(() => { throw Error('Page reload timeout'); })]);
  };
  const select = id => evaluate('document.querySelector(' + JSON.stringify('[aria-label="Otvori ' + id + '"]') + ').click()');
  const openCase = async id => {
    await select(id); await wait("!!document.querySelector('[data-investigation-open]')");
    await evaluate("document.querySelector('[data-investigation-open]').click()");
    await wait("!!document.querySelector('[data-start]:not(:disabled)')");
  };
  const get = async path => { const response = await fetch('http://127.0.0.1:8000' + path); assert.equal(response.status,200); return response.json(); };
  const attemptPath = id => '/api/investigation/attempts/' + id;
  const restart = async scenario => { stop(backend); await pause(300); env.INVESTIGATION_TEST_SCENARIO = scenario; backend = startBackend(); await ready('http://127.0.0.1:8000/api/health'); };
  const startRun = async () => { await evaluate("document.querySelector('[data-start]').click()"); await wait("!!document.querySelector('[data-run-state=created]')"); };
  await tab.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3");
  await openCase('CASE-001');
  assert((await evaluate('document.body.innerText')).includes('Nema sačuvane istrage'));
  assert.equal(worker().state, 'idle'); note('Opening report panel reads only; no automatic enqueue');
  await startRun();
  const response = await fetch('http://127.0.0.1:5173/api/investigation/runs?case_id=CASE-001'); assert.equal(response.status,200);
  const queued = (await response.json()).items[0]; report.attempt_id = queued.attempt_id;
  assert.equal(queued.state,'created'); assert.equal(queued.budget.provider_requests,0);
  note('Explicit browser start -> proxy/API queued attempt; no dispatch', queued.attempt_id);
  assert.equal(worker().state,'ready_for_review'); await wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  const done = await get(attemptPath(queued.attempt_id));
  assert.equal(done.provider_mode,'test'); assert.equal(done.budget.provider_requests,4);
  assert.deepEqual(done.trace.map(t=>t.name),['get_case_facts','get_account_history','search_procedures']);
  assert(done.trace.every(t=>t.status==='completed')); assert.equal(done.report.semantic_review,'not_reviewed');
  assert((await evaluate('document.body.innerText')).includes('TEST provider'));
  assert((await evaluate('document.body.innerText')).includes('Semantički pregled: na čekanju'));
  report.trace=done.trace; note('Actual separate worker executes three tools and persists validated report',done.budget);
  const items=[];
  for (const step of done.trace) for (const id of step.evidence_refs) {
    const item=await get(attemptPath(done.attempt_id)+'/evidence/'+id);
    assert.equal(item.attempt_id,done.attempt_id); assert.equal(item.context_revision,done.context_revision); items.push(item);
  }
  assert.deepEqual([...new Set(items.map(e=>e.kind))].sort(),['case_fact','history','procedure']);
  for (const id of done.report.draft.citations) {
    const item=items.find(e=>e.evidence_id===id); assert(item);
    await evaluate('document.querySelector('+JSON.stringify('[data-evidence="'+id+'"]')+').click()');
    await wait('Array.from(document.querySelectorAll("pre")).some(p=>p.textContent===' + JSON.stringify(item.text) + ')');
    const content=await evaluate('document.body.innerText'); assert(content.includes(item.text));
    if (item.passage) { assert(content.includes(item.passage.text)); assert(content.includes(item.passage.document.source_uri)); assert(content.includes(item.passage.document.jurisdiction)); }
  }
  note('API exact bound facts/history/procedure; browser inspects exact cited text and provenance');
  await reload(); await wait("document.querySelectorAll('.case-choice').length===3"); await openCase('CASE-001');
  await wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  const unchanged=await get(attemptPath(done.attempt_id)); assert.equal(unchanged.budget.provider_requests,4); assert.equal(unchanged.report.report_id,done.report.report_id);
  note('Browser reload opens saved report with zero new provider requests');
  await restart('invalid_citation'); await startRun();
  const invalid=worker(); assert.equal(invalid.state,'failed'); await wait("!!document.querySelector('[data-run-state=failed]')");
  const failed=await get(attemptPath(invalid.attempt_id)); assert.equal(failed.failure.code,'output_invalid'); assert.equal(failed.budget.repairs,1); assert.equal(failed.report,null);
  assert((await evaluate('document.body.innerText')).includes('output_invalid'));
  note('Invalid citation: one repair then controlled failed state, no report',invalid.attempt_id);
  await restart('needs_information'); await openCase('CASE-002'); await startRun();
  assert.equal(worker().state,'needs_information'); await wait("!!document.querySelector('[data-run-state=needs_information]')");
  assert((await evaluate('document.body.innerText')).includes('Nedostajuće informacije'));
  note('Actual no-match/missing-information report visible for a separate case');
  stop(backend); await pause(300); env.INVESTIGATION_ENABLED='false'; env.INVESTIGATION_STORE=join(work,'missing.sqlite'); backend=startBackend(); await ready('http://127.0.0.1:8000/api/health');
  await reload(); await wait("document.querySelectorAll('.case-choice').length===3");
  for (const id of ['CASE-001','CASE-002','CASE-003']) {
    await select(id); await wait("!!document.querySelector('.risk-score')"); assert.equal(await evaluate("document.querySelectorAll('[role=alert]').length"),0);
    await evaluate("document.querySelector('.button-back').click()"); await wait("!document.querySelector('.risk-score')");
  }
  for (const base of ['http://127.0.0.1:8000','http://127.0.0.1:5173']) { assert.equal((await fetch(base+'/api/cases/CASE-999')).status,404); assert.equal((await fetch(base+'/api/cases/CASE-1')).status,422); }
  note('Original three-case list/detail/back and API/proxy 404/422; feature off, no corpus/key/model');
  assert.equal(report.errors.length,0); note('No uncaught browser exceptions'); report.status='PASS';
} catch (error) { report.status='FAIL'; report.failure=String(error.stack??error); try { report.last_ui = (await tab.send('Runtime.evaluate', {expression:'document.body.innerText',returnByValue:true})).result.value; } catch {} process.exitCode=1; }
finally {
  try { await browser?.send('Browser.close'); } catch {} tab?.ws.close(); browser?.ws.close();
  for (const child of owned.reverse()) { try { stop(child); } catch (error) { report.cleanup_error=String(error); } }
  try { for (const port of [8000,5173,9228]) await free(port); report.owned_process_cleanup = 'PASS'; } catch (error) { report.cleanup_error=String(error); }
  if (report.cleanup_error) { report.status='FAIL'; process.exitCode=1; }
  await writeFile('evidence/tasks/feature-003-fixture-journey-results.json',JSON.stringify(report,null,2)+'\n'); console.log(JSON.stringify(report,null,2));
  process.exit(process.exitCode??0);
}
