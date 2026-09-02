#!/usr/bin/env node
/*
 * probe-source.mjs -- the SOURCE channel of the motion-graphics grader
 * (grading-rubric.md section 4.1).
 *
 * The HyperFrames contract makes state a pure function of timeline time, so a
 * composition does not have to be inferred from pixels: it can be interrogated.
 * Load index.html in headless Chrome, wait for the fonts and for the timeline
 * to register, then for every frame f call tl.pause(); tl.seek(f / fps) and
 * read every element that any tween targets.
 *
 * Writes two files into --out:
 *   tracks.json  per element per frame -- rect, transforms, paint, text length
 *   tweens.json  the tween table once -- absolute start, duration, ease samples
 *
 * usage: node probe-source.mjs <composition-dir> --fps 30 --out <dir>
 *
 * Three things the rubric gets wrong or leaves out, corrected here and reported
 * in the output so a reader can see the deviation:
 *
 *  1. window.__timelines is an OBJECT keyed by composition id, not an array.
 *     The rubric says `tl = window.__timelines[0]`, which is undefined on every
 *     real composition. We take Object.entries() and pick the root id.
 *  2. Nothing in a standalone composition creates window.__timelines -- the
 *     render host does. Loading index.html directly therefore throws on the
 *     registration line and the page reports no timeline at all. We install the
 *     registry with Page.addScriptToEvaluateOnNewDocument, before page script.
 *  3. The ease is sampled at 101 points ALWAYS, not only when vars.ease is a
 *     function. A downstream grader written in Python cannot evaluate
 *     "power2.out" without shipping GSAP; the samples are the portable form.
 */

import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME_CANDIDATES = [
  process.env.CHROME_PATH || '',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  path.join(process.env.LOCALAPPDATA || '', 'Google/Chrome/Application/chrome.exe'),
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
];

function findChrome(explicit) {
  for (const p of (explicit ? [explicit] : []).concat(CHROME_CANDIDATES)) {
    if (p && fs.existsSync(p)) return p;
  }
  throw new Error('no Chrome found - pass --chrome <path> or set CHROME_PATH');
}

function freePort() {
  return new Promise((res, rej) => {
    const s = createServer();
    s.on('error', rej);
    s.listen(0, '127.0.0.1', () => {
      const p = s.address().port;
      s.close(() => res(p));
    });
  });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* The endpoint in /json/version is the BROWSER target, which has no Runtime or
 * Page domain -- evaluating against it fails with "'Runtime.evaluate' wasn't
 * found", which reads like a Chrome version problem and is not one. The page
 * target from /json/list is the one to attach to. */
async function waitForPageTarget(port, timeoutMs) {
  const end = Date.now() + timeoutMs;
  let lastErr = 'no response';
  while (Date.now() < end) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/json/list`);
      if (r.ok) {
        const list = await r.json();
        const page = list.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
        if (page) return page;
        lastErr = `no page target among ${list.length} targets`;
      }
    } catch (e) { lastErr = e.message; }
    await sleep(150);
  }
  throw new Error(`Chrome DevTools gave no page target on port ${port} within ${timeoutMs} ms (${lastErr})`);
}

// ---------------------------------------------------------------- CDP client
class CDP {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.events = [];
    ws.onmessage = (ev) => {
      const msg = JSON.parse(typeof ev.data === 'string' ? ev.data : ev.data.toString());
      if (msg.id !== undefined) {
        const p = this.pending.get(msg.id);
        if (p) { this.pending.delete(msg.id); p(msg); }
      } else {
        this.events.push(msg);
      }
    };
  }
  static async connect(wsUrl) {
    const ws = new WebSocket(wsUrl);
    await new Promise((res, rej) => {
      ws.onopen = res;
      ws.onerror = () => rej(new Error('CDP websocket failed to open'));
    });
    return new CDP(ws);
  }
  send(method, params = {}, timeoutMs = 600000) {
    const id = ++this.id;
    return new Promise((res, rej) => {
      const t = setTimeout(() => {
        this.pending.delete(id);
        rej(new Error(`CDP ${method} timed out after ${timeoutMs} ms`));
      }, timeoutMs);
      this.pending.set(id, (msg) => { clearTimeout(t); res(msg); });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  /** Evaluate in the page and return the value, throwing page errors as errors. */
  async evalIn(expression, { awaitPromise = false, timeoutMs = 600000 } = {}) {
    const r = await this.send('Runtime.evaluate', {
      expression, returnByValue: true, awaitPromise, allowUnsafeEvalBlockedByCSP: true,
    }, timeoutMs);
    if (r.error) throw new Error(`CDP error: ${JSON.stringify(r.error)}`);
    const d = r.result;
    if (d.exceptionDetails) {
      const e = d.exceptionDetails;
      throw new Error(`page threw: ${e.exception?.description || e.text}`);
    }
    return d.result.value;
  }
  takeEvents(method) {
    return this.events.filter((e) => e.method === method);
  }
  close() { try { this.ws.close(); } catch { /* already gone */ } }
}

// -------------------------------------------------------------- page payload
// Everything below runs inside the composition. It is a string rather than a
// function so it can be sent verbatim through Runtime.evaluate.

const PAGE_SETUP = String.raw`
(function () {
  // A cap on the text elements pulled in beyond the tween targets. Every
  // element costs a getBoundingClientRect and a getComputedStyle on every
  // frame, so an unbounded sweep of a deep DOM would multiply the probe's
  // running time; 400 is more cards than any film in the library has.
  const MAX_EXTRA_TEXT = 400;
  const GSAP_CONFIG = new Set(['duration','ease','delay','stagger','repeat','yoyo','yoyoEase',
    'repeatDelay','repeatRefresh','immediateRender','overwrite','onComplete','onStart','onUpdate',
    'onRepeat','onReverseComplete','onInterrupt','callbackScope','id','data','paused','runBackwards',
    'startAt','lazy','keyframes','inherit','parent','smoothChildTiming','autoRemoveChildren',
    'defaults','scrollTrigger','motionPath','onCompleteParams','onStartParams','onUpdateParams',
    'onRepeatParams','onReverseCompleteParams']);

  function cssPath(el) {
    if (el.id) return '#' + el.id;
    const parts = [];
    let n = el;
    while (n && n.nodeType === 1 && parts.length < 8) {
      if (n.id) { parts.unshift('#' + n.id); break; }
      const p = n.parentElement;
      if (!p) { parts.unshift(n.tagName.toLowerCase()); break; }
      const sibs = Array.prototype.filter.call(p.children, (c) => c.tagName === n.tagName);
      const i = sibs.indexOf(n) + 1;
      parts.unshift(n.tagName.toLowerCase() + (sibs.length > 1 ? ':nth-of-type(' + i + ')' : ''));
      n = p;
    }
    return parts.join('>');
  }

  const registry = window.__timelines || {};
  const ids = Object.keys(registry);
  // The registry is an OBJECT keyed by composition id. The rubric's [0] is
  // wrong; on every real composition it is undefined.
  const roots = Array.prototype.slice.call(document.querySelectorAll('[data-composition-id]'));
  const outer = roots.filter((r) => !r.parentElement || !r.parentElement.closest('[data-composition-id]'));
  const rootEl = outer[0] || roots[0] || null;
  const rootId = rootEl ? rootEl.getAttribute('data-composition-id') : null;
  const chosenId = (rootId && registry[rootId]) ? rootId : ids[0];
  const tl = registry[chosenId];
  if (!tl) return { ok: false, reason: 'no timeline registered', ids: ids };
  // The fallback recovers a usable timeline, but a composition that registers
  // an ARRAY is a contract violation and the run has to say so: on a file with
  // two registered timelines the same fallback could attach to the wrong one.
  const contract = (rootId && !registry[rootId])
    ? ('the composition registers window.__timelines as '
       + (Array.isArray(registry) ? 'an array' : 'an object with keys ' + JSON.stringify(ids))
       + '; the contract is window.__timelines["' + rootId + '"] = tl')
    : null;

  const tweens = tl.getChildren(true, true, false);

  // Element table: every element that any tween targets, plus enough DOM
  // context for the secondary-motion criterion to find parents and siblings.
  const elMap = new Map();
  const parentIds = new Map();
  const els = [];
  function keyFor(el) {
    if (elMap.has(el)) return elMap.get(el);
    const idx = els.length;
    elMap.set(el, idx);
    let pIdx = -1;
    if (el.parentElement) {
      if (!parentIds.has(el.parentElement)) parentIds.set(el.parentElement, parentIds.size);
      pIdx = parentIds.get(el.parentElement);
    }
    const clipEl = el.closest ? el.closest('.clip,[data-start]') : null;
    els.push({
      i: idx,
      key: cssPath(el),
      id: el.id || null,
      tag: el.tagName,
      cls: el.className && el.className.baseVal !== undefined ? el.className.baseVal : (el.className || ''),
      clip: clipEl ? (clipEl.id || cssPath(clipEl)) : null,
      parentIdx: pIdx,
      text: (el.textContent || '').trim().slice(0, 80),
      depth: (function () { let d = 0, n = el; while (n.parentElement) { d++; n = n.parentElement; } return d; })(),
      _el: el,
    });
    return idx;
  }

  const tweenRows = [];
  for (let ti = 0; ti < tweens.length; ti++) {
    const tw = tweens[ti];
    // Absolute start: walk the parent chain and sum, stopping at the root
    // timeline (whose own startTime is meaningless here).
    let start = tw.startTime();
    let p = tw.parent;
    while (p && p !== tl) { start += p.startTime(); p = p.parent; }

    const targets = tw.targets().filter((t) => t && t.nodeType === 1);
    const tKeys = targets.map(keyFor);

    // Sample the parsed ease at 101 points, whatever form it took. A string
    // ease is unusable downstream without shipping GSAP; the samples are not.
    let easeFn = tw._ease;
    if (typeof easeFn !== 'function' && window.gsap && gsap.parseEase) {
      try { easeFn = gsap.parseEase(tw.vars && tw.vars.ease); } catch (e) { easeFn = null; }
    }
    let samples = null;
    if (typeof easeFn === 'function') {
      samples = [];
      for (let k = 0; k <= 100; k++) samples.push(+easeFn(k / 100).toFixed(6));
    }
    const easeStr = (tw.vars && typeof tw.vars.ease === 'string') ? tw.vars.ease
      : (tw.vars && tw.vars.ease ? 'function' : 'none');

    const vk = Object.keys(tw.vars || {});
    const props = vk.filter((k) => !GSAP_CONFIG.has(k));
    const plain = (o) => {
      const out = {};
      for (const k of Object.keys(o || {})) {
        const v = o[k];
        if (typeof v === 'function' || typeof v === 'object') continue;
        out[k] = v;
      }
      return out;
    };

    tweenRows.push({
      i: ti,
      start: +start.toFixed(6),
      duration: +tw.duration().toFixed(6),
      repeat: (tw.repeat && tw.repeat()) || 0,
      easeString: easeStr,
      easeSamples: samples,
      targets: tKeys,
      varsKeys: vk,
      props: props,
      to: plain(tw.vars),
      startAt: tw.vars && tw.vars.startAt ? plain(tw.vars.startAt) : null,
      immediateRender: tw.vars ? tw.vars.immediateRender : undefined,
    });
  }

  // Text that no tween targets is still on screen and still has to be read.
  // The element table used to hold tween targets only, so a card built as a
  // plain <div>work</div> inside a clip that is cut in and cut out -- no tween
  // anywhere on the element -- was invisible to every text criterion. Those
  // are exactly the SHORTEST cards in a hard-cut film and exactly the ones the
  // readability criterion exists to catch: three of them ran 14, 16 and 20
  // frames and none was measured. They are marked tweened:false so the
  // grader can tell where their window has to come from.
  const textScope = rootEl || document.body;
  const SKIP_TAGS = { SCRIPT: 1, STYLE: 1, TITLE: 1, HEAD: 1, META: 1, LINK: 1 };
  const before = els.length;
  const scan = textScope.querySelectorAll('*');
  for (let i = 0; i < scan.length && els.length < before + MAX_EXTRA_TEXT; i++) {
    const el = scan[i];
    if (SKIP_TAGS[el.tagName]) continue;
    if (elMap.has(el)) continue;
    let own = 0;
    for (let k = 0; k < el.childNodes.length; k++) {
      const nd = el.childNodes[k];
      if (nd.nodeType === 3) own += (nd.nodeValue || '').replace(/\s+/g, '').length;
    }
    if (own > 0) keyFor(el);
  }
  for (let i = before; i < els.length; i++) els[i].tweened = false;
  for (let i = 0; i < before; i++) els[i].tweened = true;

  // DOM ancestry AMONG TWEEN TARGETS, resolved after the tween walk because an
  // ancestor is often added to the table after its own descendants. C3's onset
  // census counts sub-groups as one element, so it needs a real parent chain;
  // parentIdx indexes a separate map and cannot be walked.
  const elIndex = new Map();
  els.forEach(function (e, i) { elIndex.set(e._el, i); });
  els.forEach(function (e) {
    const clipEl = e._el.closest ? e._el.closest('.clip,[data-start]') : null;
    let near = -1, top = -1;
    // the ".clip sub-group": the outermost ancestor STRICTLY inside the clip,
    // or the element itself when it is a direct child of the clip. Four
    // headline words in four mask wrappers are one sub-group; four separate
    // lines that are direct children of the clip are four.
    let sub = e._el;
    let n = e._el.parentElement;
    while (n) {
      if (clipEl && n === clipEl) break;
      if (!clipEl) { sub = e._el; break; }
      if (elIndex.has(n)) {
        if (near < 0) near = elIndex.get(n);
        top = elIndex.get(n);
      }
      sub = n;
      n = n.parentElement;
    }
    e.parent = near;
    e.group = top >= 0 ? top : e.i;
    e.subGroup = (sub.id ? '#' + sub.id : cssPath(sub));
  });

  window.__probe = {
    tl: tl,
    els: els,
    n: 0,
    num: els.map(() => []),
    styleRuns: els.map(() => ({})),
    charRuns: els.map(() => []),
    ownCharRuns: els.map(() => []),
    lineRuns: els.map(() => []),
  };

  return {
    ok: true,
    // the DOM composition id, not the registry key: a composition that
    // registers an array reported its timeline as composition "0"
    compositionId: rootId || chosenId,
    registryKey: chosenId,
    contractWarning: contract,
    registryIds: ids,
    skippedIds: ids.filter((k) => k !== chosenId),
    tlDuration: +tl.duration().toFixed(6),
    tweens: tweenRows,
    elements: els.map((e) => ({
      i: e.i, key: e.key, id: e.id, tag: e.tag, cls: e.cls, clip: e.clip,
      parentIdx: e.parentIdx, parent: e.parent, group: e.group,
      subGroup: e.subGroup, text: e.text, depth: e.depth,
      tweened: e.tweened !== false,
    })),
    root: rootEl ? {
      id: rootId,
      width: +(rootEl.getAttribute('data-width') || 0),
      height: +(rootEl.getAttribute('data-height') || 0),
      fps: +(rootEl.getAttribute('data-fps') || 0),
      duration: +(rootEl.getAttribute('data-duration') || 0),
    } : null,
    clips: Array.prototype.map.call(document.querySelectorAll('[data-start]'), function (c) {
      return {
        id: c.id || cssPath(c),
        start: +c.getAttribute('data-start'),
        duration: +(c.getAttribute('data-duration') || 0),
      };
    }),
  };
})()
`;

// The per-frame sampler. Kept as a separate evaluate so the frame loop can be
// chunked and report progress instead of blocking on one giant call.
const PAGE_SAMPLE = String.raw`
(function (f0, f1, fps) {
  const P = window.__probe;
  const NUM = ['x','y','xPercent','yPercent','scale','scaleX','scaleY','rotation','opacity'];
  const STY = ['filter','clipPath','color','backgroundColor','fontSize','fontWeight','visibility'];
  const tl = P.tl;
  const r2 = (v) => (typeof v === 'number' && isFinite(v)) ? +v.toFixed(3) : 0;
  // One Range, reused. The number of LINE BOXES an element's own text occupies
  // is the only honest test of whether it wraps: a box-height multiple of the
  // font size fires on every masked word rise, because a .wm mask wrapper is
  // routinely 1.8 to 2.1 times the font size, and that misrouted seventeen of
  // eighteen reading units on a finished film into the body-copy model.
  const RG = document.createRange();

  for (let f = f0; f < f1; f++) {
    tl.pause();
    tl.seek(f / fps);
    for (let i = 0; i < P.els.length; i++) {
      const el = P.els[i]._el;
      const r = el.getBoundingClientRect();
      const g = [];
      for (let k = 0; k < NUM.length; k++) {
        let v = 0;
        try { v = parseFloat(gsap.getProperty(el, NUM[k])); } catch (e) { v = 0; }
        g.push(r2(v));
      }
      // rect first (cx, cy, w, h), then the gsap properties
      P.num[i].push(r2(r.left + r.width / 2), r2(r.top + r.height / 2), r2(r.width), r2(r.height),
        g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8]);

      const cs = getComputedStyle(el);
      const runs = P.styleRuns[i];
      for (let k = 0; k < STY.length; k++) {
        const name = STY[k];
        const v = cs[name];
        let a = runs[name];
        if (!a) { a = runs[name] = []; }
        if (!a.length || a[a.length - 1][1] !== v) a.push([f, v]);
      }
      const c = (el.textContent || '').replace(/\s+/g, '').length;
      const ca = P.charRuns[i];
      if (!ca.length || ca[ca.length - 1][1] !== c) ca.push([f, c]);
      // Characters in this element's OWN text nodes, not its descendants'. A
      // container whose words are per-word spans is not a text element; the
      // spans are. Without the distinction a full-bleed word wall reports as a
      // 112-character line running at 420 characters per second.
      let own = 0;
      for (let k = 0; k < el.childNodes.length; k++) {
        const nd = el.childNodes[k];
        if (nd.nodeType === 3) own += (nd.nodeValue || '').replace(/\s+/g, '').length;
      }
      const oa = P.ownCharRuns[i];
      if (!oa.length || oa[oa.length - 1][1] !== own) oa.push([f, own]);
      let lines = 0;
      if (own > 0) {
        try {
          RG.selectNodeContents(el);
          const rs = RG.getClientRects();
          const tops = {};
          for (let k = 0; k < rs.length; k++) {
            if (rs[k].width < 0.5 || rs[k].height < 0.5) continue;
            tops[Math.round(rs[k].top)] = 1;
          }
          lines = Object.keys(tops).length;
        } catch (e) { lines = 0; }
      }
      const la = P.lineRuns[i];
      if (!la.length || la[la.length - 1][1] !== lines) la.push([f, lines]);
    }
    P.n = f + 1;
  }
  return P.n;
})(F0, F1, FPS)
`;

// ------------------------------------------------------------------- main
function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t.startsWith('--')) {
      const k = t.slice(2);
      const v = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : 'true';
      a[k] = v;
    } else a._.push(t);
  }
  return a;
}

function resolveEntry(target) {
  const st = fs.existsSync(target) ? fs.statSync(target) : null;
  if (!st) throw new Error(`composition not found: ${target}`);
  if (st.isDirectory()) {
    const idx = path.join(target, 'index.html');
    if (!fs.existsSync(idx)) throw new Error(`no index.html in ${target}`);
    return idx;
  }
  return target;
}

/** Sub-composition hosts embed other compositions; probing them measures the
 *  wrapper, not the motion, so they are skipped by name rather than graded. */
function isSubCompositionHost(html) {
  if (/<hf-composition|<hf-comp\b/i.test(html)) return 'contains an <hf-composition> host element';
  if (/data-composition-src\s*=/i.test(html)) return 'contains data-composition-src';
  const roots = html.match(/data-composition-id\s*=/gi) || [];
  if (roots.length > 1) return `declares ${roots.length} composition roots`;
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args._.length) {
    console.error('usage: node probe-source.mjs <composition-dir> --fps 30 --out <dir>');
    process.exit(2);
  }
  const entry = resolveEntry(args._[0]);
  const outDir = args.out || path.join(path.dirname(entry), '.probe');
  const timeoutS = +(args.timeout || 45);
  fs.mkdirSync(outDir, { recursive: true });

  const html = fs.readFileSync(entry, 'utf8');
  const hostReason = isSubCompositionHost(html);
  if (hostReason) {
    const skip = { skipped: true, reason: `sub-composition host: ${hostReason}`, entry };
    fs.writeFileSync(path.join(outDir, 'tracks.json'), JSON.stringify(skip));
    fs.writeFileSync(path.join(outDir, 'tweens.json'), JSON.stringify(skip));
    console.error(`skip: ${skip.reason}`);
    return 0;
  }

  const m = (re) => { const r = html.match(re); return r ? r[1] : null; };
  const declW = +(m(/data-width="([\d.]+)"/) || 1280);
  const declH = +(m(/data-height="([\d.]+)"/) || 720);
  const declFps = +(m(/data-fps="([\d.]+)"/) || 30);
  const declDur = +(m(/data-duration="([\d.]+)"/) || 0);
  const fps = +(args.fps || declFps || 30);
  const duration = +(args.duration || declDur);
  if (!duration) throw new Error('composition declares no data-duration and none was passed with --duration');
  const nFrames = Math.round(duration * fps);

  const chrome = findChrome(args.chrome);
  const port = await freePort();
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'probe-chrome-'));
  const proc = spawn(chrome, [
    '--headless=new', '--disable-gpu', '--hide-scrollbars', '--mute-audio',
    '--no-first-run', '--no-default-browser-check', '--disable-extensions',
    '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
    '--allow-file-access-from-files', '--force-device-scale-factor=1',
    `--window-size=${declW},${declH}`,
    `--user-data-dir=${profile}`,
    `--remote-debugging-port=${port}`,
    'about:blank',
  ], { stdio: 'ignore' });

  let cdp = null;
  const cleanup = () => {
    if (cdp) cdp.close();
    try { proc.kill(); } catch { /* already dead */ }
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch { /* leave it */ }
  };
  process.on('exit', cleanup);

  try {
    const target = await waitForPageTarget(port, 25000);
    cdp = await CDP.connect(target.webSocketDebuggerUrl);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Log.enable').catch(() => {});
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: declW, height: declH, deviceScaleFactor: 1, mobile: false,
    });
    // The registry is created by the render host, not by the composition, so a
    // standalone index.html throws on its own registration line without this.
    await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
      source: 'window.__timelines = window.__timelines || {};',
    });

    const url = pathToFileURL(entry).href;
    await cdp.send('Page.navigate', { url });

    const end = Date.now() + timeoutS * 1000;
    let loaded = false;
    while (Date.now() < end && !loaded) {
      if (cdp.takeEvents('Page.loadEventFired').length) loaded = true;
      else await sleep(100);
    }
    if (!loaded) console.error(`warning: no load event within ${timeoutS}s, probing anyway`);

    await cdp.evalIn('document.fonts.ready.then(() => true)', { awaitPromise: true });

    // Wait for the timeline. document.fonts.ready resolving is not the same as
    // the composition's own .then() having run.
    let ready = false;
    while (Date.now() < end) {
      ready = await cdp.evalIn(
        'typeof window.__timelines === "object" && window.__timelines !== null && Object.keys(window.__timelines).length > 0');
      if (ready) break;
      await sleep(200);
    }
    if (!ready) {
      const diag = await cdp.evalIn(`JSON.stringify({
        gsap: typeof window.gsap,
        registry: typeof window.__timelines,
        keys: window.__timelines ? Object.keys(window.__timelines) : null,
        roots: Array.prototype.map.call(document.querySelectorAll('[data-composition-id]'), (e)=>e.getAttribute('data-composition-id')),
      })`);
      const errs = cdp.takeEvents('Runtime.exceptionThrown')
        .map((e) => e.params.exceptionDetails?.exception?.description || e.params.exceptionDetails?.text)
        .slice(0, 5);
      throw new Error(
        `no GSAP timeline registered on window.__timelines within ${timeoutS}s.\n` +
        `  entry: ${entry}\n  page state: ${diag}\n` +
        (errs.length ? `  page errors:\n    ${errs.join('\n    ')}\n` : '') +
        '  The composition must do window.__timelines[<id>] = tl on a paused timeline.');
    }

    const setup = await cdp.evalIn(PAGE_SETUP);
    if (!setup || !setup.ok) {
      throw new Error(`timeline setup failed: ${JSON.stringify(setup)}`);
    }
    console.error(`composition "${setup.compositionId}", ${setup.elements.length} tween targets, ` +
      `${setup.tweens.length} tweens, ${nFrames} frames @ ${fps} fps`);
    if (setup.contractWarning) {
      console.error(`warning: HyperFrames contract violation - ${setup.contractWarning}`);
    }
    if (setup.skippedIds.length) {
      console.error(`skipped sub-composition timelines: ${setup.skippedIds.join(', ')}`);
    }

    const CHUNK = 60;
    for (let f = 0; f < nFrames; f += CHUNK) {
      const f1 = Math.min(f + CHUNK, nFrames);
      const expr = PAGE_SAMPLE.replace('F0', String(f)).replace('F1', String(f1)).replace('FPS', String(fps));
      await cdp.evalIn(expr);
      if (f % 300 === 0 || f1 === nFrames) process.stderr.write(`  frames ${f1}/${nFrames}\r`);
    }
    process.stderr.write('\n');

    // Read the payload out in slices; one 8 MB Runtime.evaluate return value is
    // where the websocket transport starts to be the bottleneck.
    const len = await cdp.evalIn(`
      window.__pj = JSON.stringify({
        num: window.__probe.num,
        styleRuns: window.__probe.styleRuns,
        charRuns: window.__probe.charRuns,
        ownCharRuns: window.__probe.ownCharRuns,
        lineRuns: window.__probe.lineRuns
      }); window.__pj.length;`);
    const SLICE = 4 * 1024 * 1024;
    let json = '';
    for (let o = 0; o < len; o += SLICE) {
      json += await cdp.evalIn(`window.__pj.slice(${o}, ${o + SLICE})`);
    }
    const payload = JSON.parse(json);

    const tracks = {
      composition: setup.compositionId,
      registryKey: setup.registryKey,
      contractWarning: setup.contractWarning,
      entry: path.resolve(entry),
      fps,
      frames: nFrames,
      duration,
      width: declW,
      height: declH,
      declaredFps: declFps,
      timelineDuration: setup.tlDuration,
      numericProps: ['cx', 'cy', 'w', 'h', 'x', 'y', 'xPercent', 'yPercent',
        'scale', 'scaleX', 'scaleY', 'rotation', 'opacity'],
      styleProps: ['filter', 'clipPath', 'color', 'backgroundColor', 'fontSize', 'fontWeight', 'visibility'],
      elements: setup.elements,
      clips: setup.clips,
      root: setup.root,
      num: payload.num,
      styleRuns: payload.styleRuns,
      charRuns: payload.charRuns,
      ownCharRuns: payload.ownCharRuns,
      lineRuns: payload.lineRuns,
    };
    fs.writeFileSync(path.join(outDir, 'tracks.json'), JSON.stringify(tracks));
    fs.writeFileSync(path.join(outDir, 'tweens.json'), JSON.stringify({
      composition: setup.compositionId,
      fps,
      frames: nFrames,
      elements: setup.elements,
      clips: setup.clips,
      tweens: setup.tweens,
    }, null, 1));
    const kb = (p) => Math.round(fs.statSync(path.join(outDir, p)).size / 1024);
    console.error(`wrote ${outDir}/tracks.json (${kb('tracks.json')} KB), tweens.json (${kb('tweens.json')} KB)`);
    return 0;
  } finally {
    cleanup();
  }
}

main().then((c) => process.exit(c)).catch((e) => {
  console.error(`probe-source: ${e.message}`);
  process.exit(1);
});
