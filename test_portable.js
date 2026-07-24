// Boots the portable page from its own blob AND simulates typing, since the
// input path is exactly what went untested before.
const fs = require('fs');
const html = fs.readFileSync(process.argv[2] || 'lost_kingdom_portable.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '', keyHandler = null;
function mkEl(id) {
  return { id, textContent: '', value: '', placeholder: '', disabled: false,
    scrollTop: 0, scrollHeight: 0, className: '', style: {},
    appendChild(n) { if (id === 'term') { captured += n.textContent; process.stdout.write(n.textContent); } },
    addEventListener(ev, fn) { if (id === 'cmd' && ev === 'keydown') keyHandler = fn; },
    focus() {} };
}
const els = {};
global.document = { body: { style: {} },
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: () => ({ textContent: '', className: '' }) };

new Function(script)();   // page calls boot() itself

function type(text) {
  if (!keyHandler) return;
  els.cmd.value = text;
  keyHandler({ key: 'Enter' });
}

let sent = 0;
const iv = setInterval(() => {
  if (captured.includes('(Y/N)') && sent === 0) { sent = 1; type('y'); }
  else if (captured.includes('Ramshackle') && sent === 1) { sent = 2; type('look'); }
}, 300);

setTimeout(() => {
  clearInterval(iv);
  console.log('\n---');
  console.log('background from same blob :', String(document.body.style.backgroundImage).startsWith('url(data:image/png;base64,'));
  console.log('banner                    :', captured.includes('Lost Kingdom'));
  console.log('copyright                 :', captured.includes('Jon Ripley'));
  console.log('reached prompt            :', captured.includes('Enable long room descriptions'));
  console.log('ACCEPTED INPUT (y)        :', captured.includes('Ramshackle'));
}, 100000);
