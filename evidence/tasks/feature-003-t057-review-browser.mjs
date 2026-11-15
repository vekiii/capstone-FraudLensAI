// Phase 6 actual browser sessions/proxy/API/CLI. Automated TEST operator only.
import { spawn, execFileSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { resolve, join, relative } from 'node:path';
import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';
const root = process.cwd(); const work = join(root, '.cache', '003-review-browser-' + randomUUID());
assert(process.argv.slice(2).every(arg => arg === '--reviewed'));
const report = { mode: 'Phase 6 automated review UI/API; authored fixture/test provider; not human approval or LLM evaluation', work, checks: [], errors: [], requests: [] };
const owned = []; const pause = ms => new Promise(r => setTimeout(r, ms));
let browser, tab, secondTab, setup;
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
function startBackend() { return start(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-review-runtime.py', work, 'api']); }
async function free(port) { await new Promise((ok, no) => { const s = createServer(); s.once('error', no); s.listen(port, '127.0.0.1', () => s.close(ok)); }); }
async function ready(url) { for (let i = 0; i < 80; i++) { try { const r = await fetch(url); if (r.ok) return; } catch {} await pause(100); } throw Error('Service unavailable: ' + url); }
async function connect(url) {
  const ws = new WebSocket(url); let seq = 0; const pending = new Map(); const listeners = new Map();
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = event => no(event.error ?? Error('WebSocket connection failed: ' + url)); });
  ws.onmessage = ({ data }) => { const message = JSON.parse(data); if (message.id) { const p = pending.get(message.id); if (p) { clearTimeout(p.timer); pending.delete(message.id); message.error ? p.reject(Error(JSON.stringify(message.error))) : p.resolve(message.result); } } else for (const fn of listeners.get(message.method) ?? []) fn(message.params); };
  return { ws, on(name, fn) { listeners.set(name, [...(listeners.get(name) ?? []), fn]); }, send(method, params = {}) { return new Promise((resolve, reject) => { const id = ++seq; const timer = setTimeout(() => { pending.delete(id); reject(Error('CDP timeout: ' + method)); }, 10000); pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params })); }); } };
}

const helper = 'evidence/tasks/feature-003-review-runtime.py';
const worker = () => JSON.parse(execFileSync(join(root, '.venv/Scripts/python.exe'), [helper, work, 'worker'], { env, windowsHide: true, encoding: 'utf8' }).trim());
try {
  for (const port of [8000, 5173, 9228]) await free(port);
  await mkdir(work, { recursive: true });
  execFileSync(join(root, '.venv/Scripts/python.exe'), ['evidence/tasks/feature-003-knowledge-smoke-prepare.py', work], { env, windowsHide: true });
  setup = JSON.parse(await readFile(join(work, 'setup.json'), 'utf8')); env.INVESTIGATION_STORE = setup.store;
  startBackend();
  start(process.execPath, ['frontend/node_modules/vite/bin/vite.js', 'frontend', '--config', 'frontend/vite.config.ts', '--host', '127.0.0.1', '--port', '5173', '--strictPort']);
  await ready('http://127.0.0.1:8000/api/health'); await ready('http://127.0.0.1:5173/');
  start('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', '--disable-gpu', '--disable-extensions', '--disable-background-networking', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=9228', '--user-data-dir=' + join(work, 'chrome-profile'), '--no-first-run', '--no-default-browser-check', 'about:blank']);
  await ready('http://127.0.0.1:9228/json/version');
  const version = await (await fetch('http://127.0.0.1:9228/json/version')).json(); report.browser = version.Browser;
  browser = await connect(version.webSocketDebuggerUrl);
  async function session() {
    const { browserContextId } = await browser.send('Target.createBrowserContext');
    const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank', browserContextId });
    const targets = await (await fetch('http://127.0.0.1:9228/json/list')).json();
    const connection = await connect(targets.find(t => t.id === targetId).webSocketDebuggerUrl);
    await connection.send('Page.enable'); await connection.send('Runtime.enable'); await connection.send('Network.enable');
    connection.on('Runtime.exceptionThrown', v => report.errors.push(v.exceptionDetails));
    connection.on('Network.responseReceived', v => { if (v.response.url.includes('/api/investigation/')) report.requests.push({ session: browserContextId, url: v.response.url, status: v.response.status }); });
    const evaluate = async expression => { const v = await connection.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }); if (v.exceptionDetails) throw Error(JSON.stringify(v.exceptionDetails)); return v.result.value; };
    const wait = async expression => { for (let i = 0; i < 160; i++) { if (await evaluate(expression)) return; await pause(50); } throw Error('Browser timeout: ' + expression); };
    const click = selector => evaluate('document.querySelector(' + JSON.stringify(selector) + ').click()');
    const open = async () => { await connection.send('Page.navigate', { url: 'http://127.0.0.1:5173/' }); await wait("document.querySelectorAll('.case-choice').length===3"); await click('[aria-label="Otvori CASE-001"]'); await wait("!!document.querySelector('[data-investigation-open]')"); await click('[data-investigation-open]'); await wait("!!document.querySelector('[data-start]:not(:disabled)')"); };
    const fill = (disposition, rationale, correction = '') => evaluate(`document.querySelector('[data-disposition]').value=${JSON.stringify(disposition)};document.querySelector('[data-rationale]').value=${JSON.stringify(rationale)};document.querySelector('[data-correction-note]').value=${JSON.stringify(correction)};`);
    const submit = () => evaluate("document.querySelector('[data-review-form]').requestSubmit()");
    return { connection, evaluate, wait, click, open, fill, submit, context: browserContextId };
  }
  const a = await session(), b = await session(); tab = a.connection; secondTab = b.connection;
  report.sessions = [a.context, b.context]; assert.notEqual(a.context, b.context);
  const get = async path => { const response = await fetch('http://127.0.0.1:8000' + path); assert.equal(response.status, 200); return response.json(); };
  const path = run => '/api/investigation/attempts/' + run.attempt_id;
  const latest = async () => (await get('/api/investigation/runs?case_id=CASE-001')).items[0];
  const createReady = async () => { await a.click('[data-start]'); await a.wait("!!document.querySelector('[data-run-state=created]')"); const created = await latest(); const done = worker(); assert.equal(done.attempt_id, created.attempt_id); assert.equal(done.state, 'ready_for_review'); await a.click('[data-refresh]'); await a.wait("!!document.querySelector('[data-run-state=ready_for_review]')"); return get(path(created)); };
  const postReview = async (run, body, key = randomUUID()) => fetch('http://127.0.0.1:8000' + path(run) + '/reviews', { method: 'POST', headers: { 'Content-Type': 'application/json', 'If-Match': String(run.revision), 'Idempotency-Key': key }, body: JSON.stringify(body) });
  const requestBody = (run, disposition = 'close') => ({ report_id: run.report.report_id, disposition, rationale: 'AUTOMATED fixture API check', correction_note: null, supersedes_review_id: null });

  const stimuli = JSON.parse(await readFile('evals/investigation/inputs/safety.json','utf8'));
  const injected = stimuli.find(x=>x.id==='SAFE-02').stimulus.case_text;
  const script = await a.connection.send('Page.addScriptToEvaluateOnNewDocument', { source: `
    const savedFetch = window.fetch;
    window.fetch = async (...args) => {
      const response = await savedFetch(...args);
      if (String(args[0]).split('?')[0].endsWith('/api/cases/CASE-001')) {
        const payload = await response.clone().json();
        payload.risk_assessment.explanation = ${JSON.stringify(injected)};
        return new Response(JSON.stringify(payload), {status:200,headers:{'content-type':'application/json'}});
      }
      return response;
    };` });
  await a.connection.send('Page.navigate',{url:'http://127.0.0.1:5173/'});
  await a.wait("document.querySelectorAll('.case-choice').length===3");
  await a.click('[aria-label="Otvori CASE-001"]');
  await a.wait('document.body.innerText.includes('+JSON.stringify(injected)+')');
  assert.equal(await a.evaluate('window.pwned === undefined'),true);
  note('SAFE-02 exact case injection rendered literally in real browser; script never executed');
  await a.connection.send('Page.removeScriptToEvaluateOnNewDocument',{identifier:script.identifier});

  await a.open(); const original = await createReady(); await b.open(); await b.wait("!!document.querySelector('[data-run-state=ready_for_review]')");
  assert.equal(await a.evaluate("document.querySelector('[data-disposition]').value"), '');
  const beforeInvalid = await latest(); await a.fill('close', '   '); await a.submit(); await pause(150);
  assert.deepEqual(await latest(), beforeInvalid);
  const invalid = await postReview(original, { ...requestBody(original), rationale: ' ' }); assert.equal(invalid.status, 422);
  const forged = await postReview(original, { ...requestBody(original), actor: 'forged' }); assert.equal(forged.status, 422);
  const wrongReport = await postReview(original, { ...requestBody(original), report_id: 'f'.repeat(64) }); assert.equal(wrongReport.status, 409);
  note('Explicit empty decision, whitespace rationale, forged actor and wrong report are rejected without review writes');
  const citation = original.report.draft.citations[0], exact = await get(path(original) + '/evidence/' + citation);
  await a.click('[data-evidence="' + citation + '"]'); await a.wait('Array.from(document.querySelectorAll("pre")).some(p=>p.textContent===' + JSON.stringify(exact.text) + ')');
  note('Original bound citation inspected in actual browser', { attempt: original.attempt_id, evidence: citation });
  // Retain exact fixture review input/key for a real same-key HTTP replay later.
  await a.evaluate(`window.reviewRequests=[];window.originalFetch=window.fetch;window.fetch=async(...args)=>{if(String(args[0]).endsWith('/reviews'))window.reviewRequests.push({url:args[0],options:args[1]});return window.originalFetch(...args);};`);
  await a.fill('close', 'AUTOMATED fixture close; no human approval'); await a.submit(); await a.wait("!!document.querySelector('[data-run-state=reviewed]')");
  const first = await latest(); assert.equal(first.review.disposition, 'close'); assert(first.review.actor.startsWith('AUTOMATED TEST OPERATOR')); assert.deepEqual(first.report.draft, original.report.draft);
  await b.fill('escalate', 'AUTOMATED stale second session'); await b.submit(); await b.wait("document.body.innerText.includes('revision_conflict')");
  assert.equal(await b.evaluate("document.querySelector('[data-review-submit]').disabled"), true);
  assert.deepEqual(await latest(), first);
  note('Two independent browser contexts: one close accepted, stale escalate rejected 409 without overwrite', { attempt: first.attempt_id, accepted_review: first.review.review_id, revision: first.revision });
  await b.click('[data-refresh]'); await b.wait("!!document.querySelector('[data-run-state=reviewed]')");
  const correction = '<img src=x onerror=alert(1)> AUTOMATED literal correction';
  await b.fill('escalate', 'AUTOMATED changed interpretation', correction); await b.submit(); await b.wait('document.body.innerText.includes(' + JSON.stringify(correction) + ')');
  const amended = await latest(); assert.equal(amended.review.supersedes_review_id, first.review.review_id); assert.equal(amended.revision, first.revision + 1); assert.equal(amended.review.disposition, 'escalate'); assert.deepEqual(amended.report.draft, original.report.draft); assert.deepEqual(amended.budget, original.budget);
  assert.equal(await b.evaluate('document.querySelectorAll("img").length'), 0);
  const replay = await a.evaluate(`(async()=>{const saved=window.reviewRequests[0];const r=await window.originalFetch(saved.url,saved.options);return {status:r.status,body:await r.json()};})()`);
  assert.equal(replay.status, 201); assert.deepEqual(replay.body, first); assert.deepEqual(await latest(), amended);
  note('Explicit refresh, linked correction, safe literal note and original response replay after amendment', { original: first.review, amendment: amended.review });
  await a.click('[data-refresh]'); await a.wait('document.body.innerText.includes(' + JSON.stringify(correction) + ')');
  const second = await createReady(); await a.fill('escalate', 'AUTOMATED initial escalate'); await a.submit(); await a.wait("!!document.querySelector('[data-run-state=reviewed]')"); assert.equal((await latest()).review.disposition, 'escalate');
  const third = await createReady(); await a.fill('request_more_information', 'AUTOMATED initial request for facts'); await a.submit(); await a.wait("!!document.querySelector('[data-run-state=reviewed]')"); assert.equal((await latest()).review.disposition, 'request_more_information');
  note('All three initial dispositions saved and reopened through actual UI', [first.attempt_id, second.attempt_id, third.attempt_id]);
  const needsCreated = JSON.parse(execFileSync(join(root, '.venv/Scripts/python.exe'), [helper, work, 'needs'], { env, windowsHide: true, encoding: 'utf8' }).trim());
  const needsDone = worker(); assert.equal(needsDone.attempt_id, needsCreated.attempt_id); assert.equal(needsDone.state, 'needs_information'); const needs = await get(path(needsCreated));
  await a.click('[data-refresh]'); await a.wait("!!document.querySelector('[data-run-state=needs_information]')");
  assert.deepEqual(await a.evaluate("Array.from(document.querySelectorAll('[data-disposition] option')).map(o=>o.value)"), ['', 'request_more_information']);
  for (const disposition of ['close', 'escalate']) { const denied = await postReview(needs, requestBody(needs, disposition)); assert.equal(denied.status, 409); assert.equal((await denied.json()).error.code, 'invalid_transition'); }
  await a.fill('request_more_information', 'AUTOMATED needs-information limitation'); await a.submit(); await a.wait("!!document.querySelector('[data-run-state=reviewed]')");
  const needsReview = await latest(); const invalidAmendment = await postReview(needsReview, { ...requestBody(needs, 'close'), supersedes_review_id: needsReview.review.review_id, correction_note: 'AUTOMATED forbidden close' }); assert.equal(invalidAmendment.status, 409);
  note('Saved limitations draft permits request-more-information only, including after review', { attempt: needs.attempt_id, report: needs.report.report_id });
  await a.open(); await a.wait("!!document.querySelector('[data-run-state=reviewed]')"); assert((await a.evaluate('document.body.innerText')).includes(needsReview.review.review_id));
  const audit = JSON.parse(execFileSync(join(root, '.venv/Scripts/python.exe'), [helper, work, 'audit'], { env, windowsHide: true, encoding: 'utf8' }).trim());
  assert.equal(audit.reports.length, 4); assert.equal(audit.reviews.length, 5);
  const history = audit.audit_events.filter(event => event.operation === 'analyst_review'); assert.equal(history.length, 5);
  assert.deepEqual(audit.reviews.slice(0, 2), [first.review, amended.review]);
  for (const run of [original, second, third, needs]) { const stored = audit.reports.find(r => r.attempt_id === run.attempt_id); assert.deepEqual(stored.draft, run.report.draft); const reopened = await get(path(run)); assert.deepEqual(reopened.report.draft, run.report.draft); assert.deepEqual(reopened.budget, run.budget); }
  report.audit = { review_events: history, review_count: audit.reviews.length, report_count: audit.reports.length, review_request_keys: audit.request_keys.filter(k => k.operation === 'review').map(({ actor, operation, request_key }) => ({ actor, operation, request_key })) };
  report.human_confirmation = { status: 'PENDING', analyst_identity: null, human_review_date: null, reason: 'All stored actions in this run were generated by the automated test operator.' };
  note('Reopen and SQLite audit: five immutable review events, four unchanged drafts, stable budgets, no duplicate replay');
  assert.equal(report.errors.length, 0); note('No uncaught exceptions in either browser session'); report.status = 'PASS';
} catch (error) { report.status = 'FAIL'; report.failure = String(error.stack ?? error); try { report.last_ui = (await tab.send('Runtime.evaluate', { expression: 'document.body.innerText', returnByValue: true })).result.value; } catch {} process.exitCode = 1; }
finally {
  try { await browser?.send('Browser.close'); } catch {} tab?.ws.close(); secondTab?.ws.close(); browser?.ws.close();
  for (const child of owned.reverse()) { try { stop(child); } catch (error) { report.cleanup_error = String(error); } }
  try { for (const port of [8000, 5173, 9228]) { for (let i = 0; ; i++) { try { await free(port); break; } catch (error) { if (i >= 40) throw error; await pause(100); } } } report.owned_process_cleanup = 'PASS'; } catch (error) { report.cleanup_error = String(error); }
  if (report.cleanup_error) { report.status = 'FAIL'; process.exitCode = 1; }
  await writeFile('evidence/tasks/feature-003-t057-review-browser-results.json', JSON.stringify(report, null, 2) + '\n'); console.log(JSON.stringify(report, null, 2));
  process.exit(process.exitCode ?? 0);
}
