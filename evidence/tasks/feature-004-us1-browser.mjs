// Automated local fixture walkthrough; isolated Chrome profile, owned processes only.
import { spawn, execFileSync } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { createServer } from 'node:net';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';

const root=process.cwd(), work=join(root,'.cache','004-us1-browser-'+randomUUID());
const report={mode:'Automated Chrome real API/proxy/UI; bundled synthetic source, not human review',checks:[],errors:[],work};
const owned=[], pause=ms=>new Promise(r=>setTimeout(r,ms));
const env={...process.env,UV_CACHE_DIR:join(root,'.cache/uv'),SPECIFY_FEATURE_DIRECTORY:'specs/004-simulation-and-prioritization',APP_MODE:'fixture'};
let browser,tab;
function note(name,detail){report.checks.push({name,status:'PASS',detail});}
function start(program,args){const child=spawn(program,args,{cwd:root,env,windowsHide:true,stdio:['ignore','pipe','pipe']});owned.push(child);child.stdout.on('data',()=>{});child.stderr.on('data',()=>{});return child;}
async function free(port){await new Promise((ok,no)=>{const s=createServer();s.once('error',no);s.listen(port,'127.0.0.1',()=>s.close(ok));});}
async function ready(url){for(let i=0;i<100;i++){try{if((await fetch(url)).ok)return;}catch{}await pause(100);}throw Error('Unavailable: '+url);}
async function connect(url){const ws=new WebSocket(url);let seq=0;const pending=new Map(),listeners=new Map();await new Promise((ok,no)=>{ws.onopen=ok;ws.onerror=no;});ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=pending.get(m.id);if(p){clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}}else for(const fn of listeners.get(m.method)??[])fn(m.params);};return {ws,on(name,fn){listeners.set(name,[...(listeners.get(name)??[]),fn]);},send(method,params={}){return new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method));},10000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));});}};}
try{
  for(const port of [8000,5173,9228])await free(port);
  await mkdir(work,{recursive:true});
  start('uv',['run','--locked','uvicorn','fraudlens.main:app','--app-dir','backend/src','--host','127.0.0.1','--port','8000']);
  start('cmd.exe',['/c','npm.cmd --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort']);
  await ready('http://127.0.0.1:8000/api/health');await ready('http://127.0.0.1:5173/');
  for(const base of ['http://127.0.0.1:8000','http://127.0.0.1:5173']){
    assert.equal((await fetch(base+'/api/health')).status,200);
    const catalog=await (await fetch(base+'/api/simulation/scenarios')).json(),s=catalog.items[0];
    const recipe={contract_version:1,scenario:{scenario_id:s.scenario_id,scenario_version:s.scenario_version,content_sha256:s.content_sha256},...s.defaults,strategy_versions:{fifo:1,highest_score:1,weighted_score_per_minute:1}};
    const response=await fetch(base+'/api/simulation/comparisons',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(recipe)});assert.equal(response.status,200);const result=await response.json();
    assert.deepEqual(result.strategies.map(r=>r.windows[0].reviewed_alert_ids),[['A'],['B'],['C','E']]);
    assert.deepEqual(result.strategies.map(r=>r.counts.outcomes.positives_found),[0,1,1]);
    assert.deepEqual(result.strategies.map(r=>r.counts.outcomes.positives_missed_threshold),[1,1,1]);
    assert.deepEqual(result.strategies.map(r=>r.counts.outcomes.positives_missed_backlog),[2,1,1]);
    assert.deepEqual(result.strategies.map(r=>r.counts.outcomes.reviewed_negatives),[1,0,1]);
    assert.deepEqual(result.strategies.map(r=>r.counts.backlog),[3,3,2]);
    assert(result.admitted_alerts.every(a=>!('outcome' in a)&&!('label' in a)));
    assert.equal((await fetch(base+'/api/cases/CASE-999')).status,404);assert.equal((await fetch(base+'/api/cases/CASE-1')).status,422);
    note('Actual API/proxy defaults, counts, privacy and original404/422',{base,scenario:s.scenario_id,hash:s.content_sha256,recipe:result.recipe});
  }
  start('C:/Program Files/Google/Chrome/Application/chrome.exe',['--headless=new','--disable-gpu','--disable-background-networking','--disable-extensions','--remote-debugging-address=127.0.0.1','--remote-debugging-port=9228','--user-data-dir='+join(work,'chrome-profile'),'--no-first-run','--no-default-browser-check','about:blank']);
  await ready('http://127.0.0.1:9228/json/version');const version=await(await fetch('http://127.0.0.1:9228/json/version')).json();report.browser=version.Browser;browser=await connect(version.webSocketDebuggerUrl);
  const {targetId}=await browser.send('Target.createTarget',{url:'about:blank'});const tabs=await(await fetch('http://127.0.0.1:9228/json/list')).json();tab=await connect(tabs.find(t=>t.id===targetId).webSocketDebuggerUrl);await tab.send('Page.enable');await tab.send('Runtime.enable');tab.on('Runtime.exceptionThrown',v=>report.errors.push(v.exceptionDetails));
  const evaluate=async expression=>{const r=await tab.send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  const wait=async expression=>{for(let i=0;i<100;i++){if(await evaluate(expression))return;await pause(50);}throw Error('Condition timeout: '+expression);};
  const click=async selector=>{assert(await evaluate(`!!document.querySelector(${JSON.stringify(selector)})`));await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);};
  await tab.send('Page.navigate',{url:'http://127.0.0.1:5173/'});await wait("document.querySelectorAll('.case-choice').length===3");note('Cases remains default view');
  await click('nav button:nth-child(2)');await wait("document.querySelectorAll('select option').length===1");assert((await evaluate('document.body.innerText')).includes('bundled_synthetic'));assert((await evaluate('document.body.innerText')).includes('illustrative_score'));note('Normal navigation/source/assumptions rendered');
  const started=Date.now();await click('[data-simulation-run]');await wait("document.querySelectorAll('[data-strategy-id]').length===3");
  const rows=await evaluate("Array.from(document.querySelectorAll('[data-strategy-id]')).map(r=>[r.dataset.strategyId,...['reviewed-alerts','positives-found','missed-threshold','missed-backlog','reviewed-negatives','backlog'].map(key=>r.querySelector('[data-'+key+']').textContent)])");
  assert.deepEqual(rows,[['fifo','A','0','1','2','1','3'],['highest_score','B','1','1','1','0','3'],['weighted_score_per_minute','C,E','1','1','1','1','2']]);note('Actual browser default comparison rows',{rows,observed_ms:Date.now()-started});
  await click('nav button:first-child');await wait("document.querySelectorAll('.case-choice').length===3");await click('[aria-label="Otvori CASE-001"]');await wait("!!document.querySelector('.risk-score')");await click('.button-back');await wait("document.querySelectorAll('.case-choice').length===3");note('Original Cases detail/back after leaving simulation');
  assert.equal(report.errors.length,0);note('No uncaught browser exceptions');report.status='PASS';
}catch(error){report.status='FAIL';report.failure=String(error.stack??error);process.exitCode=1;}
finally{
  try{await browser?.send('Browser.close');}catch{}tab?.ws.close();browser?.ws.close();
  for(const child of owned.reverse()){if(child.exitCode!==null)continue;try{execFileSync('taskkill.exe',['/PID',String(child.pid),'/T','/F'],{windowsHide:true,stdio:'ignore'});}catch{try{process.kill(child.pid,0);report.cleanup_error='Owned process still alive';}catch{}}}
  try{await pause(500);for(const port of [8000,5173,9228])await free(port);report.owned_cleanup='PASS';}catch(error){report.cleanup_error=String(error);}
  if(report.cleanup_error){report.status='FAIL';process.exitCode=1;}
  await writeFile('evidence/tasks/feature-004-us1-browser-results.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}
