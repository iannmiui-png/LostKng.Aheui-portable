// crawl.js — feeds a fixed command list, dumps the full transcript.
// Used to harvest room descriptions, object text, and messages for the
// Korean phrase dictionary. Runs the real portable page's VM.
const fs = require('fs');
const html = fs.readFileSync('lost_kingdom_portable.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '', keyHandler = null;
function mkEl(id) {
  return { id, textContent: '', value: '', placeholder: '', disabled: false,
    scrollTop: 0, scrollHeight: 0, className: '', style: {},
    classList: { add(){}, remove(){}, toggle(){} },
    appendChild(n) { if (id === 'term') { captured += n.textContent; this.textContent += n.textContent; } },
    addEventListener(ev, fn) { if (id === 'cmd' && ev === 'keydown') keyHandler = fn; },
    focus() {} };
}
const els = {};
global.document = { body: { style: {} },
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: () => ({ textContent: '', className: '' }) };
// ?play so the built-in demo stays off; we drive it ourselves
global.location = { search: '?play', protocol: 'file:' };

new Function(script)();

const cmds = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(x => x.length);
let i = 0, lastLen = -1, stable = 0;
function type(t) { els.cmd.value = t; keyHandler({ key: 'Enter' }); }

const iv = setInterval(() => {
  if (captured.length === lastLen) stable++; else { stable = 0; lastLen = captured.length; }
  if (stable >= 3 && i < cmds.length && /[>?]\s*$|\(Y\/N\)\s*\??\s*$/.test(captured)) {
    const c = cmds[i++];
    captured += `\n@@${c}@@\n`;
    type(c);
    stable = 0;
  } else if (stable >= 6 && i >= cmds.length) {
    clearInterval(iv);
    fs.writeFileSync(process.argv[3] || 'crawl_out.txt', captured);
    console.log('wrote ' + (process.argv[3] || 'crawl_out.txt') + ', ' + captured.length + ' chars, ' + i + ' cmds');
    process.exit(0);
  }
}, 200);

setTimeout(() => {
  clearInterval(iv);
  fs.writeFileSync(process.argv[3] || 'crawl_out.txt', captured);
  console.log('TIMEOUT wrote ' + captured.length + ' chars, sent ' + i + '/' + cmds.length);
  process.exit(0);
}, parseInt(process.argv[4] || '270000', 10));
