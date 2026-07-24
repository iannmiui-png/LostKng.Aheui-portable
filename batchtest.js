// Batch differential test: runs each generated PNG through the JS embedded in
// aheui_console.html and compares against the reference Brainfuck output.
const fs = require('fs');

const html = fs.readFileSync('aheui_console.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '';
function mkEl(id) {
  return {
    id, textContent: '', value: '', placeholder: '', disabled: false,
    scrollTop: 0, scrollHeight: 0, className: '', files: [],
    classList: { toggle() {}, add() {}, remove() {} },
    appendChild(n) { if (id === 'term') captured += n.textContent; },
    addEventListener() {}, focus() {},
  };
}
const els = {};
global.document = {
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: () => ({ textContent: '', className: '' }),
};
global.location = { protocol: 'file:' };

const api = new Function(`${script}\nreturn { decodePNG, buildGrid, buildSkip, AheuiVM };`)();

async function runCase(png, input) {
  const raw = await api.decodePNG(new Uint8Array(fs.readFileSync(png)));
  const g = api.buildGrid(raw);
  const skip = api.buildSkip(g);
  captured = '';
  const vm = new api.AheuiVM(g, skip);
  // preload input: the comma path is exactly what went untested before
  for (const ch of (input || '')) vm.q.push(ch.charCodeAt(0));
  for (let i = 0; i < 8; i++) vm.q.push(0);           // EOF = 0, matching the reference
  // If the program asks for more input than we supplied, getChar() would await
  // forever and the harness would exit silently with no result. Unblock it.
  const t = setTimeout(() => {
    vm.done = true;
    if (vm.resolve) { vm.q.push(0); const r = vm.resolve; vm.resolve = null; r(); }
  }, 15000);
  await vm.run();
  clearTimeout(t);
  return captured;
}

(async () => {
  const cases = JSON.parse(fs.readFileSync('jstest/cases.json', 'utf8'));
  let pass = 0;
  const fails = [];
  for (const c of cases) {
    let got;
    try { got = await runCase(c.png, c.input); }
    catch (e) { got = '<ERR ' + e.message + '>'; }
    if (got === c.expect) pass++;
    else fails.push({ bf: c.bf.slice(0, 50), expect: c.expect, got });
  }
  console.log(`JS console: ${pass}/${cases.length} passed`);
  for (const f of fails.slice(0, 4)) {
    console.log('  FAIL', JSON.stringify(f.bf));
    console.log('    expect', JSON.stringify(f.expect));
    console.log('    got   ', JSON.stringify(f.got));
  }
})();
