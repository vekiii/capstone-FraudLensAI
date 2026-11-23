import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {TransitionSeries, springTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {loadFont} from '@remotion/google-fonts/Inter';
import {BasicCaptions} from './basic-captions.element';
import data from './data/transactions.json';
import {C, FPS, T} from './theme';

const {fontFamily} = loadFont('normal', {weights: ['400', '700', '800'], subsets: ['latin']});
const d = data.demo;
export const SCENES = [
  {name: '01 Title', seconds: 4, step: 0},
  {name: '02 Problem', seconds: 5, step: 0},
  {name: '03 Incoming alert', seconds: 6, step: 0},
  {name: '04 Detect', seconds: 8, step: 1},
  {name: '05 Explain', seconds: 10, step: 2},
  {name: '06 Brief', seconds: 9, step: 3},
  {name: '07 Close', seconds: 6, step: 3},
] as const;
export const TOTAL_FRAMES = SCENES.reduce((sum, scene) => sum + scene.seconds * FPS, 0);
const starts = SCENES.map((_, index) => SCENES.slice(0, index).reduce((sum, scene) => sum + scene.seconds * FPS, 0));
const panel: CSSProperties = {background: C.panel, border: '1px solid #34373A', borderRadius: 24, boxShadow: '0 26px 80px #0005'};
const label: CSSProperties = {color: C.lime, fontSize: 20, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase'};
const headline: CSSProperties = {fontSize: 84, lineHeight: 1.05, letterSpacing: '-0.055em', fontWeight: 800, margin: 0};
const ease = Easing.bezier(0.18, 0.8, 0.22, 1);
const clamp = (frame: number, start: number, end: number) => interpolate(frame, [start, end], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
const enter = (frame: number, delay = 0) => spring({frame: frame - delay, fps: FPS, config: {damping: 200, stiffness: 120, mass: 0.9}, durationInFrames: 26});
const rise = (frame: number, delay = 0, y = 38): CSSProperties => ({opacity: enter(frame, delay), translate: `0 ${y * (1 - enter(frame, delay))}px`});

function Scene({name, children}: {name: string; children: ReactNode}) {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const sceneIndex = d.sceneLabels.indexOf(name);
  return <AbsoluteFill style={{color: C.text, fontFamily, overflow: 'hidden', scale: interpolate(frame, [0, SCENES[sceneIndex].seconds * fps], [1, 1.04], {extrapolateRight: 'clamp'})}}>
    <div style={{position: 'absolute', top: 62, left: 112, right: 112, display: 'flex', justifyContent: 'space-between', alignItems: 'center', ...rise(frame)}}>
      <strong style={{fontSize: 32, letterSpacing: '-0.06em'}}>{d.brand}<span style={{color: C.lime}}> ●</span></strong>
      <span style={{...label, fontSize: 16}}>{name}</span>
    </div>
    <div style={{position: 'absolute', top: 124, left: 112, right: 112, height: 1, background: '#34373A'}} />
    {children}
  </AbsoluteFill>;
}

function Background() {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, TOTAL_FRAMES], [250, 1450]);
  return <AbsoluteFill style={{background: C.bg, overflow: 'hidden'}}>
    <div style={{position: 'absolute', inset: 0, opacity: 0.14, backgroundImage: 'linear-gradient(#687078 1px, transparent 1px), linear-gradient(90deg, #687078 1px, transparent 1px)', backgroundSize: '96px 96px'}} />
    <div style={{position: 'absolute', width: 850, height: 850, left: x - 425, top: 90, borderRadius: '50%', background: 'radial-gradient(circle, #C8FF4D25 0%, transparent 68%)', filter: 'blur(42px)'}} />
  </AbsoluteFill>;
}

function Pipeline() {
  const frame = useCurrentFrame();
  const active = starts.reduce((value, start, index) => frame >= Math.max(0, start - (index ? T : 0)) ? SCENES[index].step : value, 0);
  return <div style={{position: 'absolute', bottom: 35, left: 112, right: 112, zIndex: 20, display: 'flex', alignItems: 'center', gap: 10, fontFamily}}>
    {d.pipeline.map((name, index) => <div key={name} style={{display: 'flex', alignItems: 'center', gap: 10, flex: 1}}>
      <div style={{...panel, width: '100%', height: 55, display: 'grid', placeItems: 'center', fontSize: 16, fontWeight: 800, letterSpacing: '0.15em', background: active === index ? C.lime : C.panel, color: active === index ? C.bg : C.muted, borderColor: active === index ? C.lime : '#34373A'}}>{name}</div>
      {index < 3 && <span style={{color: C.lime, fontSize: 23}}>→</span>}
    </div>)}
  </div>;
}

function Captions() {
  const captions = d.captions.map((text, i) => ({text, startMs: starts[i] * 1000 / FPS, endMs: (starts[i] + SCENES[i].seconds * FPS) * 1000 / FPS, timestampMs: null, confidence: null, pageBreakAfter: true}));
  return <div style={{position: 'absolute', bottom: 105, left: 610, zIndex: 21}}><BasicCaptions name="Demo captions" captions={captions} width={700} /></div>;
}

function DrawLine({dPath, color = C.lime, delay = 0, length = 500, dashed = false}: {dPath: string; color?: string; delay?: number; length?: number; dashed?: boolean}) {
  const frame = useCurrentFrame();
  return <path d={dPath} fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeDasharray={dashed ? '5 13' : length} strokeDashoffset={dashed ? -frame * 2 : length * (1 - clamp(frame, delay, delay + 28))} />;
}

function TitleScene() {
  const frame = useCurrentFrame();
  return <Scene name={d.sceneLabels[0]}>
    <svg style={{position: 'absolute', top: 230, left: 112}} width="120" height="120" viewBox="0 0 120 120"><DrawLine dPath="M20 95 L50 25 L70 75 L100 25" length={230} /></svg>
    <div style={{position: 'absolute', top: 378, left: 112, maxWidth: 1500, ...rise(frame, 5)}}><h1 style={{...headline, fontSize: 96}}>{d.title}</h1></div>
    <div style={{position: 'absolute', top: 740, left: 112, display: 'flex', gap: 18}}>{d.titleChips.map((chip, i) => <div key={chip} style={{...panel, ...rise(frame, 12 + i * 5, 20), padding: '16px 25px', color: i === 2 ? C.bg : C.lime, background: i === 2 && frame > 46 ? C.lime : C.panel, fontSize: 21, fontWeight: 800, letterSpacing: '0.13em'}}>{chip}</div>)}</div>
  </Scene>;
}

function ProblemScene() {
  const frame = useCurrentFrame();
  const value = Math.round(interpolate(frame, [8, 72], [0, d.statistic.value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease}));
  return <Scene name={d.sceneLabels[1]}>
    <div style={{position: 'absolute', top: 205, left: 112, ...rise(frame, 4)}}><div style={label}>{d.sectionLabels[0]}</div><div style={{fontSize: 230, fontWeight: 800, letterSpacing: '-0.08em', lineHeight: 1.05}}>{value}{d.statistic.suffix}</div><div style={{fontSize: 38, color: C.muted, width: 1050}}>{d.statistic.caption}</div></div>
    <div style={{position: 'absolute', top: 245, right: 112, width: 490, display: 'grid', gap: 17}}>{d.problemInputs.map((item, i) => <div key={item} style={{...panel, ...rise(frame, 12 + i * 6), padding: '28px 30px', fontSize: 28, fontWeight: 700}}><span style={{color: C.lime, marginRight: 20}}>0{i + 1}</span>{item}</div>)}</div>
    <div style={{position: 'absolute', left: 112, top: 838, fontSize: 19, color: C.muted, ...rise(frame, 35)}}>{d.statistic.sourceLabel}</div>
  </Scene>;
}

function TransactionCard({compact = false}: {compact?: boolean}) {
  const ex = d.example;
  return <div style={{...panel, padding: compact ? 34 : 45, width: compact ? 560 : 1080}}>
    <div style={{...label, fontSize: 17}}>{ex.badge}</div>
    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginTop: 24}}><div style={{fontSize: compact ? 73 : 118, fontWeight: 800, letterSpacing: '-0.07em', lineHeight: 1}}>{ex.amountLabel}</div><div style={{fontSize: 22, color: C.muted}}>{d.alertPrefix} {ex.id}</div></div>
    <div style={{height: 1, background: '#34373A', margin: '27px 0'}} />
    <div style={{display: 'flex', gap: 15, fontSize: compact ? 20 : 27}}><div style={{...panel, padding: '13px 18px'}}>{ex.counterparty}</div><div style={{...panel, padding: '13px 18px'}}>{ex.typicalMultiplier.toFixed(1)}{d.typicalAmountSuffix}</div></div>
  </div>;
}

function IncomingScene() {
  const frame = useCurrentFrame();
  return <Scene name={d.sceneLabels[2]}><div style={{position: 'absolute', top: 210, left: 112, ...rise(frame)}}><div style={label}>{d.sectionLabels[1]}</div><h2 style={{...headline, marginTop: 18}}>{d.headlines[0]}</h2></div><div style={{position: 'absolute', left: 400, top: 450, opacity: enter(frame, 10), translate: `${-920 * (1 - enter(frame, 10))}px 0`}}><TransactionCard /></div></Scene>;
}

function DetectScene() {
  const frame = useCurrentFrame();
  const ex = d.example;
  const score = interpolate(frame, [52, 142], [0, ex.score], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const flagged = score >= data.threshold;
  return <Scene name={d.sceneLabels[3]}><div style={{position: 'absolute', top: 190, left: 112, ...rise(frame)}}><div style={label}>{d.sectionLabels[2]}</div><h2 style={{...headline, marginTop: 15}}>{d.headlines[1]}</h2></div>
    <div style={{position: 'absolute', left: 112 + 115 * clamp(frame, 0, 48), top: 450, scale: 0.72, transformOrigin: 'top left', ...rise(frame, 6)}}><TransactionCard compact /></div>
    <svg style={{position: 'absolute', top: 555, left: 690}} width="330" height="100"><DrawLine dPath="M10 50 H300" delay={25} length={300}/><circle cx={10 + 290 * clamp(frame, 25, 65)} cy="50" r="8" fill={C.lime}/></svg>
    <div style={{...panel, position: 'absolute', left: 1000, top: 400, width: 760, height: 385, padding: 42, ...rise(frame, 22)}}><div style={label}>{ex.model}</div><div style={{fontSize: 120, fontWeight: 800, letterSpacing: '-0.07em', color: flagged ? C.coral : C.text, marginTop: 12}}>{score.toFixed(2)}</div><div style={{position: 'relative', height: 19, background: '#34373A', borderRadius: 12}}><div style={{width: `${score * 100}%`, height: '100%', borderRadius: 12, background: flagged ? C.coral : C.lime}}/><div style={{position: 'absolute', left: `${data.threshold * 100}%`, top: -16, height: 51, width: 2, background: C.text}}/></div><div style={{display: 'flex', justifyContent: 'space-between', marginTop: 20, fontSize: 19, color: C.muted}}><span>{ex.modelQualifier}</span><span>{d.thresholdPrefix} {data.threshold.toFixed(2)}</span></div></div>
    {flagged && <div style={{position: 'absolute', top: 816, left: 1000, color: C.coral, fontSize: 26, fontWeight: 800, letterSpacing: '0.08em'}}>{d.flaggedLabel}</div>}
  </Scene>;
}

function ExplainScene() {
  const frame = useCurrentFrame();
  const positions = [[112, 310], [112, 610], [1330, 310], [1330, 610]];
  return <Scene name={d.sceneLabels[4]}><div style={{position: 'absolute', top: 185, left: 112, ...rise(frame)}}><div style={label}>{d.sectionLabels[3]}</div><h2 style={{...headline, marginTop: 14}}>{d.headlines[2]}</h2></div>
    <svg style={{position: 'absolute', top: 340, left: 600, zIndex: 0}} width="740" height="420"><DrawLine dPath="M0 20 L350 185 M0 300 L350 185 M740 20 L390 185 M740 300 L390 185" dashed delay={18}/><circle cx={370} cy={185} r={8 + 7 * Math.sin(frame / 7)} fill={C.lime} opacity={0.5}/></svg>
    {d.evidence.map((item, i) => <div key={item} style={{...panel, position: 'absolute', left: positions[i][0] + (i < 2 ? 120 : -120) * (1 - enter(frame, 12 + i * 6)), top: positions[i][1], width: 475, height: 165, padding: 28, opacity: enter(frame, 12 + i * 6), zIndex: 1}}><div style={label}>{d.sourcePrefix} 0{i + 1}</div><div style={{fontSize: 33, fontWeight: 800, marginTop: 13}}>{item}</div></div>)}
    <div style={{...panel, position: 'absolute', left: 762, top: 460, width: 400, height: 230, padding: 36, display: 'grid', alignContent: 'center', textAlign: 'center', borderColor: C.lime, ...rise(frame, 34), zIndex: 2}}><div style={{fontSize: 70, fontWeight: 800}}>{d.ragLabel}</div><div style={{fontSize: 19, color: C.lime, marginTop: 8}}>{d.rag}</div></div>
    <div style={{position: 'absolute', left: 112, top: 855, color: C.muted, fontSize: 20}}>{d.retrievalDisclaimer}</div>
  </Scene>;
}

function BriefScene() {
  const frame = useCurrentFrame();
  const brief = d.brief;
  const count = Math.floor(interpolate(frame, [26, 146], [0, brief.heading.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const bodyCount = Math.floor(interpolate(frame, [68, 195], [0, brief.body.length], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return <Scene name={d.sceneLabels[5]}><div style={{position: 'absolute', top: 185, left: 112, ...rise(frame)}}><div style={label}>{d.sectionLabels[4]}</div><h2 style={{...headline, marginTop: 13}}>{d.headlines[3]}</h2></div>
    <div style={{...panel, position: 'absolute', left: 112, top: 375, right: 112, height: 480, padding: 40, ...rise(frame, 7)}}><div style={{fontSize: 36, fontWeight: 800, minHeight: 56}}>{brief.heading.slice(0, count)}<span style={{color: C.lime, opacity: frame % 24 < 12 ? 1 : 0}}>▌</span></div><div style={{height: 1, background: '#34373A', margin: '22px 0'}}/><div style={{fontSize: 26, lineHeight: 1.42, minHeight: 112, maxWidth: 1470}}>{brief.body.slice(0, bodyCount)}</div><div style={{display: 'flex', gap: 12, marginTop: 22}}>{brief.citations.map((item, i) => <div key={item} style={{...panel, padding: '10px 17px', color: C.violet, borderColor: C.violet, fontSize: 18, ...rise(frame, 92 + i * 6, 16)}}>{item}</div>)}</div><div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 23}}><div style={{fontSize: 23, color: C.lime}}>{brief.nextStep}</div><div style={{border: `1px solid ${C.mint}`, color: C.mint, borderRadius: 18, padding: '12px 20px', fontSize: 20, fontWeight: 700}}>{brief.review}</div></div></div>
  </Scene>;
}

function CloseScene() {
  const frame = useCurrentFrame();
  return <Scene name={d.sceneLabels[6]}><div style={{position: 'absolute', top: 278, left: 112, maxWidth: 1550, ...rise(frame, 4)}}><div style={label}>{d.sectionLabels[5]}</div><h2 style={{...headline, fontSize: 112, marginTop: 26}}>{d.close.headline}</h2></div><div style={{...panel, position: 'absolute', top: 700, left: 112, padding: '23px 32px', background: C.lime, color: C.bg, fontSize: 31, fontWeight: 800, ...rise(frame, 14)}}>{d.close.cta}</div></Scene>;
}

const scenes = [<TitleScene />, <ProblemScene />, <IncomingScene />, <DetectScene />, <ExplainScene />, <BriefScene />, <CloseScene />];
const timing = springTiming({durationInFrames: T, config: {damping: 200, stiffness: 120, mass: 0.9}});
const transitions = [
  <TransitionSeries.Transition key="transition-1" presentation={fade()} timing={timing} />,
  <TransitionSeries.Transition key="transition-2" presentation={slide({direction: 'from-right'})} timing={timing} />,
  <TransitionSeries.Transition key="transition-3" presentation={wipe()} timing={timing} />,
  <TransitionSeries.Transition key="transition-4" presentation={fade()} timing={timing} />,
  <TransitionSeries.Transition key="transition-5" presentation={slide({direction: 'from-right'})} timing={timing} />,
  <TransitionSeries.Transition key="transition-6" presentation={wipe()} timing={timing} />,
];

export function FraudLensDemo() {
  const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: C.bg}}><Background /><TransitionSeries>
    {scenes.flatMap((scene, index) => [
      ...(index ? [transitions[index - 1]] : []),
      <TransitionSeries.Sequence key={SCENES[index].name} name={SCENES[index].name} durationInFrames={SCENES[index].seconds * fps + (index < SCENES.length - 1 ? T : 0)}>{scene}</TransitionSeries.Sequence>,
    ])}
  </TransitionSeries><Pipeline /><Captions /></AbsoluteFill>;
}
