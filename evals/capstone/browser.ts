// Local browser driver for EV-01 and the read-only EV-06 revisit.
import assert from 'node:assert/strict';
import { execFile, spawn, type ChildProcess } from 'node:child_process';
import { once } from 'node:events';
import { readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { join, resolve } from 'node:path';
import { setTimeout as pause } from 'node:timers/promises';
import { promisify } from 'node:util';

const execute = promisify(execFile);
const input = JSON.parse(await readFile(process.argv[2], 'utf8'));
const app = 'http://127.0.0.1:5173';
const chrome = process.env.CAPSTONE_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const result: Record<string, any> = {};
const children: ChildProcess[] = [];
let socket: WebSocket | undefined;

function start(name: string, command: string, args: string[]) {
  const child = spawn(command, args, { windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
  children.push(child);
  child.once('error', error => { result[name + '_error'] = error.code ?? error.name; });
  child.once('exit', code => { if (code) result[name + '_exit'] = code; });
  for (const stream of [child.stdout, child.stderr]) stream?.resume();
}

async function available(port: number) {
  const server = createServer().listen(port, '127.0.0.1');
  await once(server, 'listening');
  await new Promise<void>((ok, fail) => server.close(error => error ? fail(error) : ok()));
}

async function until<T>(label: string, probe: () => Promise<T | false>) {
  for (let index = 0; index < 450; index++) {
    const value = await probe();
    if (value) return value;
    await pause(100);
  }
  throw Error('Timed out: ' + label);
}

function ready(url: string) {
  return until(url, async () => {
    try { const response = await fetch(url); return response.ok && response; }
    catch { return false; }
  });
}

async function get(path: string) {
  const response = await fetch(app + path);
  assert.equal(response.status, 200, path);
  return response.json();
}

async function connect(url: string) {
  const ws = new WebSocket(url);
  socket = ws;
  await new Promise<void>((ok, fail) => { ws.onopen = () => ok(); ws.onerror = fail; });
  let sequence = 0;
  return (method: string, params = {}) => new Promise<any>((ok, fail) => {
    const id = ++sequence;
    const timer = setTimeout(() => {
      ws.removeEventListener('message', receive);
      fail(Error('CDP timeout: ' + method));
    }, 8000);
    function receive({ data }: MessageEvent) {
      const message = JSON.parse(data);
      if (message.id !== id) return;
      ws.removeEventListener('message', receive);
      clearTimeout(timer);
      if (message.error) fail(Error(message.error.message));
      else ok(message.result);
    }
    ws.addEventListener('message', receive);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

try {
  for (const port of [5173, 8000, 9229]) await available(port);
  start('api', input.python, [input.script, 'browser-api', input.phase_directory]);
  start('vite', process.execPath, [resolve('web/node_modules/vite/bin/vite.js'), 'web',
    '--config', 'web/vite.config.ts']);
  start('chrome', chrome, ['--headless=new', '--disable-gpu', '--disable-extensions', '--no-first-run',
    '--disable-background-networking', '--remote-debugging-port=9229',
    '--remote-debugging-address=127.0.0.1', '--user-data-dir=' + join(input.directory, 'chrome'), 'about:blank']);
  await ready('http://127.0.0.1:8000/api/health');
  await ready(app);
  const version = await (await ready('http://127.0.0.1:9229/json/version')).json();
  result.browser = version.Browser;
  const targets = await (await ready('http://127.0.0.1:9229/json/list')).json();
  const command = await connect(targets.find(item => item.type === 'page').webSocketDebuggerUrl);
  const evaluate = async (expression: string) => {
    const response = await command('Runtime.evaluate', { expression, returnByValue: true });
    if (response.exceptionDetails) throw Error(response.result.description);
    return response.result.value;
  };
  const wait = (selector: string) => until(selector, () =>
    evaluate('Boolean(document.querySelector(' + JSON.stringify(selector) + '))'));
  const click = async (selector: string) => {
    await wait(selector);
    await evaluate('document.querySelector(' + JSON.stringify(selector) + ').click()');
  };
  const text = (selector: string) => evaluate('document.querySelector(' + JSON.stringify(selector) + ')?.textContent');
  const openCase = async () => {
    await click('[aria-label="Otvori ' + input.case_id + '"]');
    await click('.investigation-panel > button');
  };
  const at = (state: string) => wait('[data-run-state="' + state + '"]');
  const openEvidence = async (base: string, id: string) => {
    const evidence = await get(base + '/evidence/' + id);
    await click('[data-evidence="' + id + '"]');
    if (evidence.passage) await until('exact bound passage', async () =>
      (await text('.investigation-panel')).includes(evidence.passage.text));
    return evidence;
  };

  await command('Page.navigate', { url: app + '/cases' });
  await openCase();
  const detail = await get('/api/cases/' + input.case_id + '?snapshot=' + input.snapshot);
  result.detail = detail;
  assert.equal(detail.transaction.transaction_id, input.transaction_id);
  assert.ok((await text('.risk-score')).includes(String(detail.risk_assessment.score)));
  const panel = await text('.case-panel');
  assert.ok(panel.includes(detail.risk_assessment.scorer_version) && panel.includes(detail.risk_assessment.score_kind));
  result.score_rendered = true;

  if (input.reopen) {
    const base = '/api/investigation/attempts/' + input.restore.attempt_id;
    await at('reviewed');
    assert.ok((await text('.investigation-panel')).includes(input.review.rationale));
    result.attempt = await get(base);
    assert.deepEqual(result.attempt, input.restore);
    result.opened_citations = [];
    for (const item of input.citations) {
      const evidence = await openEvidence(base, item.evidence_id);
      assert.deepEqual(evidence, item);
      result.opened_citations.push(evidence);
    }
    result.review_reopened = true;
  } else {
    await click('[data-start]:enabled');
    await at('created');
    const response = await execute(input.python, [input.script, 'worker', input.phase_directory],
      { windowsHide: true, timeout: 135000 });
    const worker = JSON.parse(response.stdout.trim());
    const base = '/api/investigation/attempts/' + worker.attempt_id;
    result.worker = worker;
    const draft = await get(base);
    result.draft_attempt = draft;
    result.attempt = draft;
    await at(draft.state);
    result.opened_citations = [];
    if (draft.report) {
      for (const id of draft.report.draft.citations) {
        const evidence = await get(base + '/evidence/' + id);
        assert.equal(evidence.attempt_id, draft.attempt_id);
        assert.equal(evidence.context_revision, draft.context_revision);
        if (evidence.passage) result.opened_citations.push(await openEvidence(base, id));
      }
      await evaluate('document.querySelector("[data-disposition]").value=' + JSON.stringify(input.review.disposition) +
        ';document.querySelector("[data-rationale]").value=' + JSON.stringify(input.review.rationale));
      await click('[data-review-submit]');
      await at('reviewed');
      result.attempt = await get(base);
      const timeOrigin = await evaluate('performance.timeOrigin');
      await command('Page.reload');
      await until('reload', () => evaluate('performance.timeOrigin !== ' + timeOrigin));
      await openCase();
      await at('reviewed');
      assert.ok((await text('.investigation-panel')).includes(input.review.rationale));
      assert.deepEqual(await get(base), result.attempt);
      result.review_reopened = true;
    }
  }
} catch (error) {
  result.error = String(error);
  process.exitCode = 1;
} finally {
  socket?.close();
  for (const child of children.reverse()) {
    if (child.pid && child.exitCode === null && child.signalCode === null) {
      const exited = once(child, 'exit');
      if (child.kill()) await exited;
    }
  }
  await writeFile(join(input.directory, 'result.json'), JSON.stringify(result, null, 2));
}
