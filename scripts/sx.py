import re


def split_top(t):
    """Split a .kicad_pcb text into its top-level s-expression children."""
    i = t.index('(kicad_pcb') + 1
    depth = 1
    n = len(t)
    instr = False
    items = []
    j = i
    last = i
    start = None
    while j < n:
        c = t[j]
        if instr:
            if c == '\\':
                j += 1
            elif c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == '(':
            if depth == 1:
                start = j
                items.append(['gap', t[last:j]])
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 1:
                items.append(['item', t[start:j + 1]])
                last = j + 1
            if depth == 0:
                return t[:i], items, t[last:]
        j += 1


def filter_top(src, dst, drop):
    head, items, tail = split_top(open(src).read())
    keep = []
    n = 0
    for kind, s in items:
        if kind == 'item' and drop(s):
            n += 1
            if keep and keep[-1][0] == 'gap':
                keep.pop()
            continue
        keep.append((kind, s))
    open(dst, 'w').write(head + ''.join(s for _, s in keep) + tail)
    return n
