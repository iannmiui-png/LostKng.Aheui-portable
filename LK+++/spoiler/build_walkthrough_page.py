#!/usr/bin/env python3
"""
build_walkthrough_page.py — produces walkthrough_portable.html: a single
self-contained file where the tall Korean parody PNG is BOTH the page
background AND the program that runs. It decodes the pure-Aheui Lost
Kingdom from those pixels, runs it live, and auto-feeds the verified
99-point walkthrough (extracted from 99point.png's embedded save) so it
plays itself to a Master, First Class finish.

Reuses the exact, tested VM from build_portable.py; only the driver changes
(feed the 99-move save instead of the herring demo), plus a live step
tracker in the corner.
"""
import base64
import re


def build(png='lost_kingdom_pure_aheui.png',
          alphabet='aheui_alphabet.txt',
          walkthrough='walkthrough_99.txt',
          out='walkthrough_portable.html',
          title='잃어버린 왕국 · 99점 공략'):
    # pull the VM + decode/grid/skip code out of the portable builder's template
    import build_portable as bp
    tmpl = bp.TEMPLATE

    b64 = base64.b64encode(open(png, 'rb').read()).decode('ascii')
    alpha = open(alphabet, encoding='utf-8').read()
    alpha_js = ''.join('\\n' if c == '\n' else c if c == ' ' else '\\u%04X' % ord(c)
                       for c in alpha)
    moves = open(walkthrough, encoding='utf-8').read().strip().split('\n')
    moves_js = '[' + ','.join('"%s"' % m for m in moves) + ']'

    # ---- take the portable template and swap the demo section ----
    html = tmpl
    html = html.replace('__B64__', b64)
    html = html.replace('__ALPHA__', alpha_js)
    html = html.replace('__TITLE__', title)
    html = html.replace('__REPO__', 'https://github.com/iannmiui-png/LostKng.Aheui-portable')

    # Replace the DEMO_SCRIPT block with the 99-move walkthrough + tracker state.
    walk_block = 'const WALK = ' + moves_js + ';\nconst MOVE_NOTE = ' + _notes_js(moves) + ';'
    html = re.sub(r'const DEMO_SCRIPT = \[.*?\];', lambda m: walk_block, html, count=1, flags=re.S)

    # Replace runDemo() with a walkthrough driver that feeds one move per prompt.
    html = re.sub(r'// Drives DEMO_SCRIPT.*?\n\}\n', lambda m: _WALK_DRIVER, html, count=1, flags=re.S)

    # onQuit: keep the redirect but also mark completion.
    # (unchanged — the walkthrough ends in Z Q Y Y which quits then restarts;
    #  we stop feeding after the moves run out and let it idle.)

    # Add the corner step-tracker panel + its CSS, and a progress line.
    html = html.replace('</style>', _TRACKER_CSS + '\n</style>')
    html = html.replace('<div id="panel">', _TRACKER_HTML + '\n<div id="panel">')

    open(out, 'w', encoding='utf-8').write(html)
    return len(html), len(moves)


def _notes_js(moves):
    ann = {
        'T3': 'take compass (+5)', 'F1': 'fill lamp (+10)', 'B1': 'light lamp (+5)',
        'F0': 'fill urn (+5)', 'H5': 'hurl herring — calm beast (+20)',
        'P': 'pray — gods pleased (+15)', 'H0': 'hurl urn — extinguish fire (+15)',
        'K4': 'kill mage (+24)', 'D0': 'drop dynamite — unblock cave',
        'T2': 'take matches', 'T1': 'take lamp', 'T0': 'take dynamite',
        'T5': 'take herring', 'T8': 'take urn', 'T4': 'take axe', 'T6': 'take crown',
        'D2': 'drop matches', 'D8': 'drop urn', 'D3': 'drop dynamite',
        'N': 'north', 'S': 'south', 'E': 'east', 'W': 'west',
        'Z': 'save game', 'Q': 'quit', 'Y': 'yes',
    }
    parts = []
    for m in moves:
        note = ann.get(m, ann.get(m[0], ''))
        parts.append('"%s"' % note.replace('"', '\\"'))
    return '[' + ','.join(parts) + ']'


_TRACKER_CSS = r'''
#track{position:fixed;top:12px;right:12px;width:230px;max-height:70vh;overflow:hidden;
  background:rgba(12,12,16,.92);border:1px solid #6b6b5c;border-radius:4px;z-index:6;
  font:11px/1.4 'D2Coding',Consolas,monospace;backdrop-filter:blur(2px)}
#track h4{background:linear-gradient(#2b2b25,#1c1c18);color:#e6d9a8;padding:6px 9px;
  border-bottom:1px solid #6b6b5c;font-size:12px;display:flex;justify-content:space-between}
#track h4 span{color:#8fd0ff}
#tracklist{overflow-y:auto;max-height:calc(70vh - 30px);padding:4px 0}
.tk{display:flex;gap:7px;padding:2px 9px;opacity:.35;transition:opacity .12s,background .12s}
.tk.on{opacity:1;background:#1c2530}.tk.done{opacity:.6}
.tk .i{color:#667;width:24px;text-align:right;flex-shrink:0}
.tk .m{color:#8fd0ff;width:26px;flex-shrink:0;font-weight:bold}
.tk .nn{color:#aab;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tk.sc .nn{color:#8fe08f}
'''

_TRACKER_HTML = r'''<div id="track"><h4>99점 공략 <span id="tkprog">0 / 0</span></h4><div id="tracklist"></div></div>'''


# Driver: feed the walkthrough one move per prompt; light up the tracker.
_WALK_DRIVER = r'''// Feeds the verified 99-point walkthrough (WALK) one move per prompt, watching
// the transcript settle exactly like a human waiting for '>' before typing.
// The walkthrough ends in Z Q Y Y, which saves, quits, and starts a new game.
function buildTracker(){
  const el=document.getElementById('tracklist');
  WALK.forEach((m,i)=>{
    const note=MOVE_NOTE[i]||'';
    const d=document.createElement('div');
    d.className='tk'+(/\+\d+/.test(note)?' sc':''); d.id='tk'+i;
    d.innerHTML='<span class="i">'+(i+1)+'</span><span class="m">'+m+'</span><span class="nn">'+note+'</span>';
    el.appendChild(d);
  });
  document.getElementById('tkprog').textContent='0 / '+WALK.length;
}
function runDemo(){
  buildTracker();
  cmdEl.placeholder='자동 공략 재생 중… (?play 로 직접 조작)';
  let i=0,lastLen=-1,stable=0;
  const el=document.getElementById('tracklist');
  const tick=setInterval(()=>{
    if(!vm||vm.done){clearInterval(tick);return;}
    const txt=termEl.textContent;
    if(txt.length===lastLen)stable++;else{stable=0;lastLen=txt.length;}
    // feed next move once output has settled at a prompt
    if(stable>=3 && i<WALK.length && /[>?]\s*$|\(Y\/N\)\s*\??\s*$/.test(txt)){
      const prev=document.getElementById('tk'+(i-1)); if(prev){prev.classList.remove('on');prev.classList.add('done');}
      const cur=document.getElementById('tk'+i); if(cur){cur.classList.add('on');cur.scrollIntoView({block:'nearest'});}
      const m=WALK[i]; i++;
      document.getElementById('tkprog').textContent=i+' / '+WALK.length;
      say(m+'\n','e');
      vm.feed(m);
      stable=0;
    }
  },200);
}
'''


if __name__ == '__main__':
    n, moves = build()
    print(f'walkthrough_portable.html written, {n:,} bytes ({n/1e6:.2f} MB), {moves} moves')
