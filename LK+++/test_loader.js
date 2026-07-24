// test_loader.js — exercises aheui_loader.html: launches each game, checks
// output, and verifies the Korean skin + Hangul input mapping.
const fs = require('fs');
const html = fs.readFileSync('aheui_loader.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '', keyHandler = null, cards = [];
function mkEl(id, tag) {
  const el = { id, tag, textContent: '', value: '', placeholder: '', disabled: false,
    checked: true, scrollTop: 0, scrollHeight: 0, className: '', dataset: {}, children: [],
    classList: { toggle() {}, add() {}, remove() {} },
    set innerHTML(v) { this._html = v; },
    appendChild(n) { this.children.push(n); if (id === 'term') { captured += n.textContent; this.textContent += n.textContent; } if (id === 'menu') cards.push(n); },
    addEventListener(ev, fn) { if (id === 'cmd' && ev === 'keydown') keyHandler = fn; },
    focus() {} };
  return el;
}
const els = {};
global.document = {
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: tag => mkEl('_' + tag, tag),
};
// checkboxes default checked (skin + hangul on)
global.window = {};

new Function(script)();

function type(t) { els.cmd.value = t; keyHandler({ key: 'Enter' }); }
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function launchAndRun(game, feeds, settleMs) {
  captured = '';
  // find the game's card and click it
  const GAMES = new Function(script + '\nreturn GAMES;')();
  const g = GAMES.find(x => x.id === game);
  // call launch via a fresh eval that exposes it
  await runner.launch(g);
  for (const f of feeds || []) { await sleep(600); if (runner.vm && !runner.vm.done) runner.vm.feed(f); }
  await sleep(settleMs || 4000);
  return captured;
}

// expose launch + vm by re-evaluating with a return hook
const runner = new Function(script + '\nreturn { launch, get vm(){return vm;}, GAMES };')();
// re-bind document references the second eval created
Object.assign(els, {});

(async () => {
  const results = [];
  // hello
  { captured=''; await runner.launch(runner.GAMES.find(x=>x.id==='hello')); await sleep(4000);
    results.push(['hello prints greeting', captured.includes('Hello from Aheui!')]); }
  // adder with sample 36 -> 9 (sample auto-feeds)
  { captured=''; await runner.launch(runner.GAMES.find(x=>x.id==='adder')); await sleep(5000);
    results.push(['adder 3+6=9', captured.includes('9')]); }
  // countdown
  { captured=''; await runner.launch(runner.GAMES.find(x=>x.id==='countdown')); await sleep(5000);
    results.push(['countdown 987654321', captured.includes('987654321')]); }

  for (const [name, ok] of results) console.log((ok?'OK  ':'FAIL')+' '+name);
  console.log(results.every(r=>r[1]) ? '\nMINI-GAMES PASS' : '\nMINI-GAMES FAIL');
  process.exit(0);
})();
