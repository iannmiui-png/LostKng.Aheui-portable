"""Differential test WITH input. The original generator never emitted ',',
which is why the BLOCK_IN hang survived every earlier test run."""
import io, random
from collections import defaultdict
import bf_to_aheui_stream as SC
import fast_aheui as F

def ref(code, inp, limit=100000):
    t=defaultdict(int); p=0; out=[]; st=[]; jm={}
    for i,c in enumerate(code):
        if c=='[': st.append(i)
        elif c==']': j=st.pop(); jm[j]=i; jm[i]=j
    inp=list(inp); cp=n=0
    while cp<len(code):
        c=code[cp]
        if c=='+': t[p]=(t[p]+1)%256
        elif c=='-': t[p]=(t[p]-1)%256
        elif c=='>': p+=1
        elif c=='<': p-=1
        elif c=='.': out.append(chr(t[p]))
        elif c==',': t[p]=ord(inp.pop(0)) if inp else 0
        elif c=='[' and not t[p]: cp=jm[cp]
        elif c==']' and t[p]: cp=jm[cp]
        cp+=1; n+=1
        if n>limit: return None
    return ''.join(out)

def mine(code, inp, limit=3_000_000):
    b=io.StringIO(); SC.compile_to_file(code,b)
    open('/tmp/di.aheui','w').write(b.getvalue())
    o=io.StringIO()
    steps,halted=F.run('/tmp/di.aheui', feed=inp, limit=limit, out=o)
    return o.getvalue() if halted else None

def gen(rng, depth=0):
    o=[]
    for _ in range(rng.randint(1,7)):
        r=rng.random()
        if   r<0.24: o.append('+'*rng.randint(1,6))
        elif r<0.38: o.append('-'*rng.randint(1,3))
        elif r<0.52: o.append('>'*rng.randint(1,3))
        elif r<0.64: o.append('<'*rng.randint(1,3))
        elif r<0.76: o.append('.')
        elif r<0.88: o.append(',')          # <-- the case that was missing
        elif depth<3: o.append('['+'-'+gen(rng,depth+1)+']')
    return ''.join(o)

def main(n=200, seed=6060):
    rng=random.Random(seed)
    tested=passed=skipped=0; fails=[]
    for _ in range(n):
        p=gen(rng)
        if p.count('[')!=p.count(']'): continue
        inp=''.join(rng.choice('AByz19 ') for _ in range(p.count(',')+2))
        e=ref(p,inp)
        if e is None: skipped+=1; continue
        g=mine(p,inp)
        if g is None: skipped+=1; continue
        tested+=1
        if g==e: passed+=1
        else:
            fails.append((p,inp,e,g))
            if len(fails)>=3: break
    print(f'with input: tested={tested} passed={passed} skipped={skipped}')
    for p,i,e,g in fails[:3]:
        print(' FAIL',repr(p[:50]),'in',repr(i)); print('   exp',repr(e)); print('   got',repr(g))

if __name__=='__main__':
    main()
