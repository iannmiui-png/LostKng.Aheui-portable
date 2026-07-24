// test_loader_lk.js — Lost Kingdom through the loader: Korean skin ON,
// Hangul input (북/서/집5/먹5), license shown twice, herring death in Korean.
const fs = require('fs');
const html = fs.readFileSync('aheui_loader.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '', keyHandler = null;
function mkEl(id, tag) {
  return { id, tag, textContent: '', value: '', placeholder: '', disabled: false,
    checked: true, scrollTop: 0, scrollHeight: 0, className: '', dataset: {}, children: [],
    classList: { toggle() {}, add() {}, remove() {} },
    set innerHTML(v) { this._html = v; },
    appendChild(n) { this.children.push(n); if (id === 'term') { captured += n.textContent; this.textContent += n.textContent; } },
    addEventListener(ev, fn) { if (id === 'cmd' && ev === 'keydown') keyHandler = fn; },
    focus() {} };
}
const els = {};
global.document = { getElementById: id => (els[id] ||= mkEl(id)), createElement: t => mkEl('_'+t, t) };
global.window = {};

const runner = new Function(script + '\nreturn { launch, get vm(){return vm;}, GAMES, toGameInput, translate };')();

const sleep = ms => new Promise(r => setTimeout(r, ms));
// simulate a human typing a Hangul command: map it, then feed the mapped ASCII
function hangulType(word) {
  const mapped = runner.toGameInput(word);
  if (runner.vm && !runner.vm.done) runner.vm.feed(mapped);
  return mapped;
}

(async () => {
  // sanity: mapping table
  const maps = [['북','n'],['서','w'],['남','s'],['집5','t5'],['먹5','c5'],['예','y'],['아니오','n']];
  console.log('— Hangul input mapping —');
  let mapOk = true;
  for (const [k,v] of maps) { const got = runner.toGameInput(k); const ok = got===v; mapOk&&=ok;
    console.log((ok?'OK  ':'FAIL')+' '+k+' -> '+got+(ok?'':' (want '+v+')')); }

  await runner.launch(runner.GAMES.find(x=>x.id==='lostkingdom'));
  await sleep(2500);   // reach prompt

  // license twice?
  const licEn = captured.includes('(C) Jon Ripley 2004, 2005');
  const licKo = captured.includes('존 리플리 2004, 2005');

  // play with Hangul: 예 (long desc) -> 북 -> 서 -> 집5 -> 먹5 -> 아니오
  const script2 = ['예','북','서','집5','먹5','아니오'];
  for (const w of script2) {
    // wait for output to settle at a prompt
    let last=-1, tries=0;
    while (tries++<40) { await sleep(300);
      if (captured.length===last && /[>?]\s*$|\(Y\/N\)|N\)\s*\?/.test(captured.slice(-40))) break;
      last=captured.length; }
    hangulType(w);
  }
  await sleep(3000);

  console.log('\n— Korean skin & play —');
  const checks = [
    ['license shown in English', licEn],
    ['license shown in Korean', licKo],
    ['room name translated (낡은 오두막)', captured.includes('낡은 오두막')],
    ['room desc translated (오두막 안)', captured.includes('나무 오두막 안')],
    ['pond translated (고인 연못)', captured.includes('고인 연못')],
    ['herring death in Korean (독이)', captured.includes('독이 있습니다')],
    ['died line in Korean', captured.includes('당신은 죽었습니다')],
    ['no raw English room text leaked', !captured.includes('ramshackle wooden hut')],
  ];
  let ok = mapOk;
  for (const [n,v] of checks) { console.log((v?'OK  ':'FAIL')+' '+n); ok&&=v; }
  console.log(ok ? '\nLOST KINGDOM KOREAN PASS' : '\nLOST KINGDOM KOREAN FAIL');

  // dump a slice for eyeballing
  const i = captured.indexOf('낡은 오두막');
  if (i>=0) console.log('\n--- sample ---\n'+captured.slice(i, i+300));
  process.exit(0);
})();
