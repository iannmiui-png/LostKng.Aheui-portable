#!/usr/bin/env python3
"""
build_loader.py — assembles aheui_loader.html: a single self-contained page
that carries several Aheui games (each a base64 PNG), a Korean translation
skin for Lost Kingdom, and a Hangul input layer.

Inputs:
  games_manifest.json   (games + base64 PNGs + metadata)
  unified_alphabet.txt  (shared symbol table for every game)
  ko_dict.js            (English->Korean phrase dictionary)
"""
import json
import re


def js_alpha(alpha):
    return ''.join('\\n' if c == '\n' else c if c == ' ' else '\\u%04X' % ord(c)
                   for c in alpha)


def build():
    games = json.load(open('games_manifest.json', encoding='utf-8'))
    alpha = open('unified_alphabet.txt', encoding='utf-8').read()

    dict_src = open('ko_dict.js', encoding='utf-8').read()
    m = re.search(r'const KO_DICT = \{.*?\n\};', dict_src, re.S)
    ko_dict_block = m.group(0)

    games_js = json.dumps(games, ensure_ascii=False)

    html = TEMPLATE
    html = html.replace('__ALPHA__', js_alpha(alpha))
    html = html.replace('/*__KO_DICT__*/', ko_dict_block)
    html = html.replace('/*__GAMES__*/', 'const GAMES = ' + games_js + ';')
    return html


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>아희 게임 로더 · Aheui Game Loader</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%}
body{background:#0e0f13;color:#e6e6e6;font:14px/1.55 'D2Coding',Consolas,monospace;
     display:flex;flex-direction:column;height:100vh}
#head{background:linear-gradient(#26262e,#191920);border-bottom:1px solid #45454f;
      padding:9px 14px;display:flex;justify-content:space-between;align-items:baseline}
#head b{color:#e6d9a8;font-size:16px}#head span{color:#8a8a96;font-size:11px}
#body{flex:1;display:flex;min-height:0}
#menu{width:230px;background:#15161b;border-right:1px solid #45454f;overflow-y:auto;padding:8px}
.card{border:1px solid #33343d;background:#1b1c22;padding:9px 10px;margin-bottom:8px;cursor:pointer;border-radius:3px}
.card:hover{border-color:#e6d9a8;background:#20212a}
.card.active{border-color:#7fc4ff;background:#1d2430}
.card h3{font-size:13px;color:#e6d9a8;margin-bottom:2px}
.card .ko{font-size:12px;color:#9fb8d8}
.card .d{font-size:10.5px;color:#7a7a86;margin-top:4px;line-height:1.4}
#stage{flex:1;display:flex;flex-direction:column;min-width:0}
#term{flex:1;overflow-y:auto;padding:12px 15px;white-space:pre-wrap;word-wrap:break-word;background:#0b0c10}
#term .e{color:#7fc4ff}#term .m{color:#7a7a86}#term .ko{color:#d8e0a8}
#ctl{border-top:1px solid #45454f;background:#14151a;padding:6px 12px;display:flex;gap:8px;align-items:center}
#ctl span{color:#e6d9a8;font-weight:bold}
#cmd{flex:1;background:#0a0b0f;border:1px solid #33343d;color:#7fc4ff;padding:5px 8px;
     font:14px/1.5 'D2Coding',Consolas,monospace;outline:none}
#cmd:focus{border-color:#7fc4ff}
#opts{border-top:1px solid #2a2b33;background:#101116;padding:4px 12px;font-size:11px;color:#8a8a96;display:flex;gap:14px;align-items:center}
label{cursor:pointer;user-select:none}input[type=checkbox]{vertical-align:-1px}
#stat{margin-left:auto}
kbd{background:#2a2b33;border:1px solid #45454f;border-radius:3px;padding:0 4px;color:#cfcfd6;font-size:10.5px}
</style>
</head>
<body>
<div id="head"><b>아희 게임 로더</b><span>Aheui Game Loader &mdash; pure-Hangul programs in PNG pixels</span></div>
<div id="body">
  <div id="menu"></div>
  <div id="stage">
    <div id="term"></div>
    <div id="opts">
      <label><input type="checkbox" id="ko" checked> 한국어 스킨 (Korean skin)</label>
      <label><input type="checkbox" id="hangul" checked> 한글 입력 (Hangul input)</label>
      <span>이동: <kbd>북</kbd><kbd>남</kbd><kbd>동</kbd><kbd>서</kbd> · 집기 <kbd>ㅈ숫자</kbd> · 먹기 <kbd>ㅁ숫자</kbd></span>
      <span id="stat">게임을 선택하세요</span>
    </div>
    <div id="ctl"><span>&gt;</span><input id="cmd" autocomplete="off" disabled placeholder="게임을 선택하세요…"></div>
  </div>
</div>
<script>
/*__GAMES__*/
const ALPHABET="__ALPHA__";
/*__KO_DICT__*/

const TERM_DIGIT=39,BASE=40,HBASE=0xAC00;
const STROKES=[0,2,4,4,2,5,5,3,5,7,9,9,7,9,9,8,4,4,6,2,4,0,3,4,3,4,4,0];

const termEl=document.getElementById('term'),cmdEl=document.getElementById('cmd'),
      statEl=document.getElementById('stat'),menuEl=document.getElementById('menu'),
      koEl=document.getElementById('ko'),hangulEl=document.getElementById('hangul');

// ── Korean skin: translate a settled block of English game output ──────────
// Longest-first over dictionary keys so multi-line room descriptions win over
// their fragments. Only whole-line / whole-block matches are replaced.
const KO_KEYS = Object.keys(KO_DICT).sort((a,b)=>b.length-a.length);
function translate(text){
  if(!koEl.checked) return text;
  let out=text;
  for(const en of KO_KEYS){
    if(out.indexOf(en)>=0) out=out.split(en).join(KO_DICT[en]);
  }
  return out;
}

// ── Hangul input: map Korean command words / jamo to the game's ASCII ──────
// The game parser only takes single letters + numbers, so this is a mapping
// layer, not a parser change. 북/남/동/서 -> n/s/e/w, verb syllables -> letters.
const HANGUL_DIR={'북':'n','남':'s','동':'e','서':'w',
  '위':'n','아래':'s','오른':'e','왼':'w'};
const HANGUL_VERB={  // leading syllable -> game verb letter
  '집':'t','들':'t',        // take
  '먹':'c','마':'c',        // consume (eat/drink)
  '버':'d',                 // drop
  '던':'h',                 // hurl
  '읽':'r',                 // read
  '살':'x','봐':'x','보':'l', // examine / look
  '태':'b',                 // burn
  '채':'f',                 // fill
  '봄':'l','둘':'l',        // look
  '가':'i',                 // inventory (지님?) -> use i
};
function toGameInput(s){
  if(!hangulEl.checked) return s;
  s=s.trim();
  if(s in HANGUL_DIR) return HANGUL_DIR[s];
  // verb + number, e.g. 집5 / 먹 5 / 집기5
  const m=s.match(/^([가-힣]+)\s*([0-9]*)$/);
  if(m){
    const head=m[1], num=m[2];
    for(const k in HANGUL_VERB){ if(head.startsWith(k)) return HANGUL_VERB[k]+num; }
    if(head in HANGUL_DIR) return HANGUL_DIR[head];
    // 예/아니오 for Y/N prompts
    if(head.startsWith('예')||head==='네') return 'y';
    if(head.startsWith('아니')) return 'n';
  }
  return s; // pass through (already ASCII, or unknown)
}

function say(t,c){const s=document.createElement('span');if(c)s.className=c;s.textContent=t;
  termEl.appendChild(s);termEl.scrollTop=termEl.scrollHeight;}
const status=t=>statEl.textContent=t;
const yieldUI=()=>new Promise(r=>setTimeout(r,0));
function b64bytes(b64){const s=atob(b64),a=new Uint8Array(s.length);
  for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a;}

async function decodePNG(bytes){
  let off=8,W=0,H=0,ch=4;const idat=[];
  while(off<bytes.length){
    const dv=new DataView(bytes.buffer,bytes.byteOffset+off,8),len=dv.getUint32(0);
    const type=String.fromCharCode(bytes[off+4],bytes[off+5],bytes[off+6],bytes[off+7]);
    const data=bytes.subarray(off+8,off+8+len);
    if(type==='IHDR'){const h=new DataView(data.buffer,data.byteOffset,data.length);
      W=h.getUint32(0);H=h.getUint32(4);const ct=data[9];ch=ct===6?4:ct===2?3:ct===4?2:1;}
    else if(type==='IDAT')idat.push(data);else if(type==='IEND')break;
    off+=12+len;
  }
  let n=0;for(const c of idat)n+=c.length;
  const comp=new Uint8Array(n);let p=0;for(const c of idat){comp.set(c,p);p+=c.length;}
  const ds=new DecompressionStream('deflate'),wr=ds.writable.getWriter();wr.write(comp);wr.close();
  const rd=ds.readable.getReader(),parts=[];let tot=0;
  for(;;){const{done,value}=await rd.read();if(done)break;parts.push(value);tot+=value.length;}
  const dec=new Uint8Array(tot);p=0;for(const c of parts){dec.set(c,p);p+=c.length;}
  const stride=W*ch,raw=new Uint8Array(W*H*ch);let s=0;
  for(let y=0;y<H;y++){
    const f=dec[s++],o=y*stride;
    for(let x=0;x<stride;x++){
      const cur=dec[s++],a=x>=ch?raw[o+x-ch]:0,b=y>0?raw[o-stride+x]:0,c2=(x>=ch&&y>0)?raw[o-stride+x-ch]:0;let v;
      switch(f){case 0:v=cur;break;case 1:v=(cur+a)&255;break;case 2:v=(cur+b)&255;break;
        case 3:v=(cur+((a+b)>>1))&255;break;
        case 4:{const pp=a+b-c2,pa=Math.abs(pp-a),pb=Math.abs(pp-b),pc=Math.abs(pp-c2);
          v=(cur+((pa<=pb&&pa<=pc)?a:(pb<=pc)?b:c2))&255;break;}default:v=cur;}
      raw[o+x]=v;
    }
  }
  return raw;
}

function buildGrid(raw){
  const NL=0;let end=raw.length;
  for(let i=0;i<raw.length;i++)if(raw[i]%BASE===TERM_DIGIT){end=i;break;}
  let rows=0;for(let i=0;i<end;i++)if(raw[i]%BASE===NL)rows++;
  const rowStart=new Int32Array(rows),rowLen=new Uint16Array(rows),data=new Uint8Array(end-rows);
  let r=0,w=0,st=0,W=0;
  for(let i=0;i<end;i++){const d=raw[i]%BASE;
    if(d===NL){rowStart[r]=st;rowLen[r]=w-st;if(w-st>W)W=w-st;st=w;r++;}else data[w++]=d;}
  const cho=new Int8Array(ALPHABET.length).fill(-1),ju=new Uint8Array(ALPHABET.length),jo=new Uint8Array(ALPHABET.length);
  for(let i=0;i<ALPHABET.length;i++){const o=ALPHABET.charCodeAt(i)-HBASE;
    if(o>=0&&o<19*21*28){cho[i]=(o/588)|0;ju[i]=((o%588)/28)|0;jo[i]=o%28;}}
  return{data,rowStart,rowLen,rows,W,cho,ju,jo};
}

function buildSkip(g){
  const{rows,W,cho,data,rowStart,rowLen}=g;
  const cell=(x,y)=>x<rowLen[y]?data[rowStart[y]+x]:1;
  const tab=new Array(W).fill(null);
  for(let x=0;x<W;x++){let n=0;for(let y=0;y<rows;y++)if(cho[cell(x,y)]>=0)n++;
    if(n>rows*0.3||n===0)continue;const a=new Int32Array(n);let k=0;
    for(let y=0;y<rows;y++)if(cho[cell(x,y)]>=0)a[k++]=y;tab[x]=a;}
  return tab;
}

class AheuiVM{
  constructor(g,skip){this.g=g;this.skip=skip;this.st=[];for(let i=0;i<28;i++)this.st.push([]);
    this.cur=0;this.x=0;this.y=0;this.dx=1;this.dy=0;this.steps=0;this.out='';this.q=[];this.resolve=null;this.done=false;}
  cell(x,y){const g=this.g;return x<g.rowLen[y]?g.data[g.rowStart[y]+x]:1;}
  feed(l){for(const c of l)this.q.push(c.charCodeAt(0));this.q.push(10);
    if(this.resolve){const r=this.resolve;this.resolve=null;r();}}
  flush(final){
    if(!this.out)return;
    let text=this.out;
    // Hold back the last partial line (no trailing newline) so a dictionary
    // phrase can't be split across two flushes -- unless this is the final
    // flush or we're about to block for input, when we must show everything.
    if(!final){
      const nl=text.lastIndexOf('\n');
      if(nl<0){return;}            // nothing complete yet; keep buffering
      const hold=text.slice(nl+1);
      text=text.slice(0,nl+1);
      this.out=hold;
    } else {
      this.out='';
    }
    say(translate(text), koEl.checked?'ko':null);
  }
  async getChar(){
    if(this.q.length)return this.q.shift();
    this.flush(true);
    cmdEl.disabled=false;cmdEl.placeholder='명령어 입력…';cmdEl.focus();status('입력 대기');
    await new Promise(r=>this.resolve=r);return this.q.shift();
  }
  advance(){const g=this.g;this.x+=this.dx;this.y+=this.dy;
    if(this.y<0)this.y=g.rows-1;else if(this.y>=g.rows)this.y=0;
    if(this.x<0)this.x=g.W-1;else if(this.x>=g.W)this.x=0;}
  async run(){
    const g=this.g,cho=g.cho,ju=g.ju,jo=g.jo,BATCH=3000000;
    while(!this.done){let left=BATCH;
      while(left-->0){
        const s=this.cell(this.x,this.y),c=cho[s];this.steps++;
        if(c<0){let n=4,moved=false;
          while(n-->0){this.advance();if(cho[this.cell(this.x,this.y)]>=0){moved=true;break;}}
          if(moved)continue;
          const t=(this.dx===0&&this.dy!==0)?this.skip[this.x]:null;
          if(t&&Math.abs(this.dy)===1){let lo=0,hi=t.length-1,res=-1;
            if(this.dy>0){while(lo<=hi){const m=(lo+hi)>>1;if(t[m]>this.y){res=t[m];hi=m-1;}else lo=m+1;}this.y=res>=0?res:t[0];}
            else{while(lo<=hi){const m=(lo+hi)>>1;if(t[m]<this.y){res=t[m];lo=m+1;}else hi=m-1;}this.y=res>=0?res:t[t.length-1];}
          }else this.advance();
          continue;}
        const v=ju[s],j=jo[s];
        if(v===0){this.dx=1;this.dy=0;}else if(v===2){this.dx=2;this.dy=0;}
        else if(v===4){this.dx=-1;this.dy=0;}else if(v===6){this.dx=-2;this.dy=0;}
        else if(v===8){this.dx=0;this.dy=-1;}else if(v===12){this.dx=0;this.dy=-2;}
        else if(v===13){this.dx=0;this.dy=1;}else if(v===17){this.dx=0;this.dy=2;}
        else if(v===18)this.dy=-this.dy;else if(v===19){this.dx=-this.dx;this.dy=-this.dy;}
        else if(v===20)this.dx=-this.dx;
        let ok=true;const S=this.st[this.cur];
        switch(c){
          case 2:if(S.length<2)ok=false;else{const a=S.pop(),b=S.pop();S.push(a===0?0:Math.trunc(b/a));}break;
          case 3:if(S.length<2)ok=false;else{const a=S.pop();S[S.length-1]+=a;}break;
          case 4:if(S.length<2)ok=false;else{const a=S.pop();S[S.length-1]*=a;}break;
          case 5:if(S.length<2)ok=false;else{const a=S.pop(),b=S.pop();S.push(a===0?0:((b%a)+a)%a);}break;
          case 6:if(!S.length)ok=false;else{const n=this.cur===21?S.shift():S.pop();
            if(j===21)this.out+=String(n);else if(j===27)this.out+=String.fromCharCode(n);}break;
          case 7:if(j===27){this.flush(true);S.push(await this.getChar());
              cmdEl.disabled=true;cmdEl.placeholder='실행 중…';status('실행 중');}
            else if(j!==21)S.push(STROKES[j]);break;
          case 8:if(!S.length)ok=false;else S.push(this.cur===21?S[0]:S[S.length-1]);break;
          case 9:this.cur=j;break;
          case 10:if(!S.length)ok=false;else{const n=this.cur===21?S.shift():S.pop();if(j!==27)this.st[j].push(n);}break;
          case 12:if(S.length<2)ok=false;else{const a=S.pop(),b=S.pop();S.push(b>=a?1:0);}break;
          case 14:if(!S.length)ok=false;else{const n=this.cur===21?S.shift():S.pop();if(n===0){this.dx=-this.dx;this.dy=-this.dy;}}break;
          case 15:if(S.length<2)ok=false;else{const t=S[S.length-1];S[S.length-1]=S[S.length-2];S[S.length-2]=t;}break;
          case 16:if(S.length<2)ok=false;else{const a=S.pop();S[S.length-1]-=a;}break;
          case 17:if(!S.length)ok=false;else{const n=this.cur===21?S[0]:S[S.length-1];if(j!==27)this.st[j].push(n);}break;
          case 18:this.done=true;break;
        }
        if(this.done)break;
        if(!ok){this.dx=-this.dx;this.dy=-this.dy;}
        this.advance();
      }
      this.flush();await yieldUI();
    }
    this.flush(true);status("프로그램 종료");cmdEl.placeholder='종료됨';cmdEl.disabled=true;
  }
}

let vm=null,curGame=null;
cmdEl.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&vm&&!vm.done){
    const raw=cmdEl.value;cmdEl.value='';
    const mapped=toGameInput(raw);
    say((raw||'')+(raw!==mapped?'  ('+mapped+')':'')+'\n','e');
    cmdEl.disabled=true;cmdEl.placeholder='실행 중…';vm.feed(mapped);
  }
});

async function launch(game){
  curGame=game;
  [...menuEl.children].forEach(c=>c.classList.toggle('active',c.dataset.id===game.id));
  termEl.textContent='';vm=null;
  // license: for Lost Kingdom show English then Korean, per requirement
  if(game.id==='lostkingdom'){
    say('Lost Kingdom\n(C) Jon Ripley 2004, 2005\nBrainfuck Edition v0.11\n','m');
    say('잃어버린 왕국\n(C) 존 리플리 2004, 2005\n브레인퍽 에디션 v0.11\n\n','m');
  }
  status('디코딩 중…');await yieldUI();
  const raw=await decodePNG(b64bytes(game.b64));
  status('격자 복원 중…');await yieldUI();
  const g=buildGrid(raw);
  say('아희 격자 '+g.rows.toLocaleString()+'행 × '+g.W+'열\n','m');
  const skip=buildSkip(g);
  say('스킵 테이블 '+skip.filter(Boolean).length+'/'+g.W+'개 열\n\n','m');
  status('실행 중');await yieldUI();
  vm=new AheuiVM(g,skip);
  vm.run();
  // auto-feed a sample for the tiny input games so they don't just block
  if(game.sample){ setTimeout(()=>{ if(vm&&!vm.done) vm.feed(game.sample); }, 400); }
}

// build the menu
GAMES.forEach(g=>{
  const d=document.createElement('div');d.className='card';d.dataset.id=g.id;
  d.innerHTML='<h3>'+g.title+'</h3><div class="ko">'+g.title_ko+'</div><div class="d">'+g.desc_ko+'</div>';
  d.onclick=()=>launch(g);
  menuEl.appendChild(d);
});
status('왼쪽에서 게임을 선택하세요 · pick a game');
</script>
</body>
</html>
"""


if __name__ == '__main__':
    html = build()
    open('aheui_loader.html', 'w', encoding='utf-8').write(html)
    print(f'aheui_loader.html written, {len(html):,} bytes ({len(html)/1e6:.2f} MB)')
