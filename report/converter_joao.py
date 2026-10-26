"""Converts report/Joao_sections_DSS_report.docx into report/conteudo_joao.ps1 (same helpers as conteudo_miguel.ps1)."""
import html
import re
import sys
import zipfile

src, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
x = z.read('word/document.xml').decode('utf-8')
body = x[x.find('<w:body>'):]

# heading in João's file -> heading title in the report outline
SECTIONS = {
    '3.1 Data Sources': 'Data Sources',
    '3.2 Stylised Facts of the BCP Stock': 'Stylised Facts of the BCP Stock',
    '3.3 Key Assumptions': 'Key Assumptions',
    '4.2.4 Fundamentalist agent type': 'Fundamentalist agent type',
    'Appendix E: Assumptions Register': 'APPENDIX E: Assumptions Register',
}
# caption text start -> reference key
KEYS = {
    'Stylised facts of the BCP stock': 'facts',
    'BCP statistics in the calm period': 'stress',
    'Key parameters, variables and functions of the Fundamentalist': 'fundParams',
    'Statechart of the Fundamentalist': 'fundChart',
    'States and transitions of the Fundamentalist': 'fundStates',
    'Assumptions register': 'assumptions',
}
# in-text references -> tokens
REFS = [('Table 9', '{T:facts}'), ('Table 10', '{T:stress}'), ('Figure X and Table X', '{F:fundChart} and {T:fundStates}')]
WIDTHS = {
    'facts': [0.8, 3.6, 5.2, 1.8, 4.6], 'stress': [4.6, 3.8, 3.8, 3.8],
    'fundParams': [3.2, 3.6, 2.6, 6.6], 'fundStates': [3.0, 5.2, 7.8],
    'assumptions': [0.8, 6.0, 2.6, 5.2, 1.4],
}


def ps(s):
    s = s.replace('’', "'").replace('\xa0', ' ')
    return "'" + s.replace("'", "''") + "'"


blocks = []  # (kind, data)
for m in re.finditer(r'<w:tbl>.*?</w:tbl>|<w:p[ >].*?</w:p>', body, re.S):
    b = m.group(0)
    if b.startswith('<w:tbl>'):
        rows = [[html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', c)))
                 for c in re.findall(r'<w:tc>.*?</w:tc>', r, re.S)]
                for r in re.findall(r'<w:tr[ >].*?</w:tr>', b, re.S)]
        blocks.append(('table', rows))
        continue
    st = re.search(r'<w:pStyle w:val="([^"]+)"', b)
    st = st.group(1) if st else ''
    t = html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', b))).strip()
    if 'r:embed=' in b:
        blocks.append(('image', None))
    if t:
        blocks.append((st, t))

lines = ["# Generated from report/Joao_sections_DSS_report.docx (João). Do not edit by hand: edit João's file and convert again.",
         "$figDirJ = Join-Path $PSScriptRoot 'figures'", ""]
section, pending_caption, bullets, refs = None, None, [], []


def flush_bullets():
    global bullets
    if bullets:
        lines.append('    Bullets @(' + ', '.join(ps(b) for b in bullets) + ')')
        bullets = []


i = 0
while i < len(blocks):
    kind, data = blocks[i]
    if kind == 'Heading1':
        flush_bullets()
        if section:
            lines.append('}')
        if data in SECTIONS:
            section = SECTIONS[data]
            lines.append('$content[%s] = {' % ps(section))
        else:  # "References to add"
            section = None
            j = i + 1
            while j < len(blocks) and blocks[j][0] == 'Compact':
                refs.append(blocks[j][1]); j += 1
            i = j
            continue
    elif kind == 'table':
        flush_bullets()
        cap_text, key = pending_caption
        hdr, rows = data[0], data[1:]
        lines.append('    Tbl %s @(%s) @(' % (ps(cap_text), ', '.join(ps(h) for h in hdr)))
        lines.append(',\n'.join('        @(' + ', '.join(ps(c) for c in r) + ')' for r in rows))
        lines.append('    ) @(%s) %s' % (', '.join(str(w) for w in WIDTHS[key]), ps(key)))
        pending_caption = None
    elif kind == 'image':
        flush_bullets()
        cap = blocks[i + 1][1]
        cap_text = re.sub(r'^Figure \S+ - ', '', cap)
        key = next(v for k, v in KEYS.items() if cap_text.startswith(k))
        lines.append("    Fig (Join-Path $figDirJ 'fundamentalist_statechart.png') %s 12.0 %s" % (ps(cap_text), ps(key)))
        i += 2
        continue
    elif kind == 'Compact':
        bullets.append(data)
    else:
        m = re.match(r'^Table \S+ - (.*)$', data)
        if m:
            cap_text = m.group(1)
            pending_caption = (cap_text, next(v for k, v in KEYS.items() if cap_text.startswith(k)))
        else:
            flush_bullets()
            for a, bref in REFS:
                data = data.replace(a, bref)
            lines.append('    Body ' + ps(data))
    i += 1
flush_bullets()
if section:
    lines.append('}')
lines.append('')
lines.append('$referencesJoao = @(' + ', '.join(ps(r) for r in refs) + ')')
open(out, 'w', encoding='utf-8-sig').write('\n'.join(lines) + '\n')
print('ok', len(lines), 'lines;', len(refs), 'references')
