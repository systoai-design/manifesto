#!/usr/bin/env node
// Reframe a measured composition into another aspect ratio.
//
// The trap this exists to prevent: hyperframes sizes the composition ROOT to
// data-width/data-height. Putting a transform on the root therefore scales a
// box that is already the output size, from its top-left corner - which throws
// the content into a corner instead of reframing it. The measured stage has to
// live in a WRAPPER inside the root, and the wrapper is what gets transformed.
//
//   node reframe.mjs index.html vertical.html --w 1080 --h 1920 --scale 1.3
//   node reframe.mjs index.html wide1080.html --w 1920 --h 1080 --scale 1.5
//
// --scale is deliberately required. Pick it with check-framing.mjs, which
// reports the widest content in the existing render: the largest safe scale is
// (targetWidth - 2*margin) / widestContent.
import fs from "node:fs";

const [, , inFile, outFile, ...rest] = process.argv;
if (!inFile || !outFile) {
  console.error("usage: reframe.mjs <in.html> <out.html> --w N --h N --scale N [--stage-w 1280] [--stage-h 720]");
  process.exit(1);
}
const arg = (k, d) => {
  const i = rest.indexOf("--" + k);
  return i >= 0 ? Number(rest[i + 1]) : d;
};
const W = arg("w"), H = arg("h"), S = arg("scale");
const SW = arg("stage-w", 1280), SH = arg("stage-h", 720);
if (!W || !H || !S) { console.error("--w, --h and --scale are all required"); process.exit(1); }

let s = fs.readFileSync(inFile, "utf8");
const was = s;

// 1. output size
s = s.replace(/data-width="\d+"\s+data-height="\d+"/, `data-width="${W}" data-height="${H}"`);

// 2. wrap everything after the media elements in the stage wrapper
const openIdx = s.search(/<div id="[a-z0-9-]+"[^>]*data-composition-id/i);
if (openIdx < 0) { console.error("no composition root found"); process.exit(1); }
// insert the wrapper after the root's opening tag, or after a trailing </audio>
const afterAudio = s.indexOf("</audio>");
if (afterAudio > openIdx) {
  s = s.slice(0, afterAudio + 8) + '\n\n  <div id="stage-wrap">' + s.slice(afterAudio + 8);
} else {
  const gt = s.indexOf(">", openIdx);
  s = s.slice(0, gt + 1) + '\n  <div id="stage-wrap">' + s.slice(gt + 1);
}
// close it before the root closes (the last </div> before <script>)
const scriptIdx = s.indexOf("<script>", s.indexOf("stage-wrap"));
const closeIdx = s.lastIndexOf("</div>", scriptIdx);
s = s.slice(0, closeIdx) + "  </div>\n" + s.slice(closeIdx);

// 3. the transform that centres the stage in the new frame
const tx = (W / 2 - (SW / 2) * S).toFixed(2);
const ty = (H / 2 - (SH / 2) * S).toFixed(2);
const tf = (Math.abs(tx) < 0.01 && Math.abs(ty) < 0.01)
  ? `scale(${S})`
  : `translate(${tx}px, ${ty}px) scale(${S})`;

// 4. strip the fixed size off the root, put it on the wrapper
const rootRe = /(#[a-z0-9-]+\s*\{\s*position:\s*relative;\s*)width:\s*\d+px;\s*height:\s*\d+px;\s*/i;
if (!rootRe.test(s)) {
  console.error("could not find the root's width/height rule - reframe by hand");
  process.exit(1);
}
s = s.replace(rootRe, `$1`);
const rootSel = s.match(/(#[a-z0-9-]+)\s*\{\s*position:\s*relative;/i)[1];
s = s.replace(
  new RegExp(`(${rootSel}\\s*\\{[^}]*\\})`, "i"),
  `$1\n  #stage-wrap { position: absolute; left: 0; top: 0; width: ${SW}px; height: ${SH}px;\n    transform: ${tf}; transform-origin: 0 0; }`
);

if (s === was) { console.error("nothing changed - check the input"); process.exit(1); }
fs.writeFileSync(outFile, s);
console.log(`${outFile}: ${W}x${H}, stage ${SW}x${SH} at ${S}x`);
console.log(`  transform: ${tf}`);
console.log(`  stage centre lands at (${(SW / 2 * S + Number(tx)).toFixed(0)}, ${(SH / 2 * S + Number(ty)).toFixed(0)}) - frame centre is (${W / 2}, ${H / 2})`);
console.log(`\nNow render it, then run check-framing.mjs on the result.`);
console.log(`Anything that ENTERS from an offset (a lockup sliding in, a line`);
console.log(`starting off-centre) can clear a 16:9 frame and clip in a narrower`);
console.log(`one - check-framing will flag it.`);
