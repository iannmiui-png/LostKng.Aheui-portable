"""
mini_games.py — original mini-games (mine), as Brainfuck source, compiled to
pure Aheui for the loader. Each is verified against a reference BF interpreter.
These are original works, distinct from Lost Kingdom.
"""

def _delta(diff):
    if diff == 0: return ''
    sign = '+' if diff > 0 else '-'
    mag = abs(diff)
    if mag < 10: return sign * mag
    for f in range(2, 16):
        g = mag // f; r = mag - f*g
        if g < 16 and abs(r) < 8:
            s = '>' + '+'*f + '[<' + sign*g + '>-]<'
            if r: s += sign*r
            return s
    return sign * mag

def text_to_bf(s):
    out=[]; prev=0
    for ch in s:
        c=ord(ch); out.append(_delta(c-prev)); out.append('.'); prev=c
    return ''.join(out)

def build_all():
    g = {}
    g['hello'] = dict(
        title='Hello Aheui', title_ko='안녕 아희',
        desc='A greeting. No input needed.', desc_ko='인사말. 입력이 필요 없습니다.',
        bf=text_to_bf('Hello from Aheui!\n'),
        input='', expect='Hello from Aheui!\n')

    g['echo'] = dict(
        title='Echo', title_ko='따라 말하기',
        desc='Type anything; it echoes back until end of input.',
        desc_ko='무엇이든 입력하세요. 입력이 끝날 때까지 그대로 따라 출력합니다.',
        bf=',[.,]', input='ahoy there\n', expect='ahoy there\n')

    g['adder'] = dict(
        title='Digit Adder', title_ko='한 자리 덧셈',
        desc='Enter two digits; prints their sum (sum must be below 10).',
        desc_ko='숫자 두 개를 입력하면 그 합을 출력합니다 (합이 10 미만일 때).',
        bf=',>,<' + '-'*48 + '[->+<]>.',
        input='36', expect='9')

    unrolled=''
    for n in range(9,0,-1):
        unrolled += '[-]' + '+'*(48+n) + '.'
    unrolled += '[-]++++++++++.'   # newline
    g['countdown'] = dict(
        title='Countdown', title_ko='카운트다운',
        desc='Counts down 9 to 1.', desc_ko='9부터 1까지 셉니다.',
        bf=unrolled, input='', expect='987654321\n')

    # Shout: read a line (until newline), store, then print it 3 times.
    # Uses a growing tape: read chars into successive cells until 10,
    # then replay. Simpler robust version: echo-with-bang — echo input,
    # then print "!!!".
    g['shout'] = dict(
        title='Shout', title_ko='외치기',
        desc='Echoes your line, then adds three exclamation marks.',
        desc_ko='입력한 줄을 따라 출력한 뒤 느낌표 세 개를 붙입니다.',
        bf=',----------[++++++++++.,----------]' + '[-]' + '+'*33 + '...',
        input='hi\n', expect='hi!!!')

    return g


if __name__ == '__main__':
    from collections import defaultdict
    def ref(code, inp, limit=5_000_000):
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

    games=build_all(); allok=True
    for name,gm in games.items():
        got=ref(gm['bf'], gm['input'])
        ok = got==gm['expect']; allok&=ok
        print(f"{'OK  ' if ok else 'FAIL'} {name:10s} in={gm['input']!r:12s} got={got!r:22s} want={gm['expect']!r}")
    print('\nALL OK:', allok)
