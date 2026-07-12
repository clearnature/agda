#!/usr/bin/env python3
"""大衍高维同构理论 · 知识图谱 SQLite 引擎 v2.1 — 多目录 + 语义边"""

import sqlite3, re, os, json, hashlib
from pathlib import Path
from datetime import datetime

SOURCE_DIRS = [
    "/home/yanli/文档/math",
    "/data/work/docs",
    "/data/trit/pyBitNet/docs",
    "/data/training/cli/scholar-loop/docs",
]
DB_PATH = "/data/work/docs/wiki/knowledge-graph.db"
EXTENSIONS = {".md", ".txt"}

KEY_TERMS = [
    'GF(3)', 'C3', 'A4', 'CRT', 'Orbit', 'Stabilizer', 'Christoffel',
    '纳音', '仲吕', '黄钟', '陈数', '时间晶体', '极限环', '声子',
    'Bézout', '幻方', 'T⁶', '144', '46', '6624', '√3', 'N14', 'Lidari',
    '全息π', '手征', 'LCM', '超流', '孤子', '十二律', 'Frobenius',
    'GF(2)', 'GF(3²)', '谱投影', '驻波', '巡游', '环面结',
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, mtime REAL, hash TEXT, indexed_at TEXT);
    CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, title TEXT, path TEXT UNIQUE, source_dir TEXT, pole TEXT, content_preview TEXT, summary TEXT);
    CREATE TABLE IF NOT EXISTS edges(id INTEGER PRIMARY KEY, from_node INTEGER REFERENCES nodes(id), to_node INTEGER REFERENCES nodes(id), relation TEXT, note TEXT, UNIQUE(from_node, to_node, relation));
    CREATE TABLE IF NOT EXISTS constants(id INTEGER PRIMARY KEY, name TEXT, value TEXT, physical_meaning TEXT, source_path TEXT, UNIQUE(name, source_path));
    CREATE TABLE IF NOT EXISTS sections(id INTEGER PRIMARY KEY, node_id INTEGER REFERENCES nodes(id), heading TEXT, level INTEGER, content_preview TEXT);
    CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(title, summary, content_preview, content=nodes, content_rowid=id);
    CREATE TRIGGER IF NOT EXISTS n_ai AFTER INSERT ON nodes BEGIN INSERT INTO nodes_fts(rowid,title,summary,content_preview) VALUES(new.id,new.title,new.summary,new.content_preview); END;
    CREATE TRIGGER IF NOT EXISTS n_ad AFTER DELETE ON nodes BEGIN INSERT INTO nodes_fts(nodes_fts,rowid,title,summary,content_preview) VALUES('delete',old.id,old.title,old.summary,old.content_preview); END;
    CREATE TRIGGER IF NOT EXISTS n_au AFTER UPDATE ON nodes BEGIN INSERT INTO nodes_fts(nodes_fts,rowid,title,summary,content_preview) VALUES('delete',old.id,old.title,old.summary,old.content_preview); INSERT INTO nodes_fts(rowid,title,summary,content_preview) VALUES(new.id,new.title,new.summary,new.content_preview); END;
    """)
    return conn

def classify_pole(path, title, content):
    t = (title + " " + content[:500]).lower(); p = path.lower()
    if any(k in t for k in ['crt','同余','bézout','bezout','gf(3)','gf3','c3','a4','代数极','galois','伽罗瓦','conjugation','共轭','谱投影','chiral','手征','算术基座','模算术']): return 'algebra'
    if any(k in t for k in ['t⁶','t6','晶格','lattice','幻方','magic','christoffel','几何极','环面','torus','测地线','螺旋','orthogonal','空间域','格点','缠绕数']): return 'geometry'
    if any(k in t for k in ['拓扑极','极限环','limit cycle','时间晶体','time crystal','陈数','chern','截断','truncation','环面结','同伦','热寂','heat death','超流','superfluid']): return 'topology'
    if any(k in t for k in ['orbit','stabilizer','轨道','稳定化子','谱投影定理','大衍','大一统','isomorphism']): return 'unification'
    if any(k in t for k in ['训练','train','384k','lcm','实验','验证','protocol','实证','benchmark','n14','lidari','泵浦']): return 'engineering'
    if any(k in t for k in ['术语','glossary','常量','constant','roadmap','路线图','知识图谱','wiki','index','体系','架构宪法']): return 'meta'
    if any(k in t for k in ['物理波','wave','phonon','声子','interference','干涉']): return 'base'
    return 'reference'

def parse_document(path, content):
    title = path.stem
    for m in re.finditer(r'^#\s+(.+)$', content, re.MULTILINE):
        title = m.group(1).strip(); break
    title = title[:120] if title else path.stem[:80]
    summary = ''
    for line in content.split('\n'):
        s = line.strip()
        if s and not s.startswith('#') and not s.startswith('>') and not s.startswith('|'):
            summary = s[:200]; break
    sections = []
    for m in re.finditer(r'^(#{1,4})\s+(.+)$', content, re.MULTILINE):
        h = m.group(2).strip()
        if len(h) > 2: sections.append((h, len(m.group(1))))
    links = []
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.(?:md|txt))\)', content):
        links.append((m.group(1), m.group(2)))
    constants = []
    in_table = False
    for line in content.split('\n'):
        if re.match(r'^\s*\|.*\|.*\|', line) and not re.match(r'^\|[\s\-:]+\|', line):
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 2:
                if any(h in cols[0].lower() for h in ('常量','参数','概念','术语','名称','constant','name')):
                    in_table = True; continue
                if in_table and cols[0] and len(cols[0]) < 60:
                    name = re.sub(r'\*\*|`','', cols[0])
                    if not re.match(r'^[\-\s]+$', name):
                        constants.append((name, cols[1] if len(cols)>1 else '', cols[2] if len(cols)>2 else ''))
            in_table = True
        else: in_table = False
    return {'title':title,'summary':summary,'sections':sections,'links':links,'constants':constants}

def resolve_link(link_path, current_dir):
    p = Path(link_path)
    if p.is_absolute(): return None
    resolved = (current_dir / p).resolve()
    if resolved.exists(): return str(resolved)
    for ext in EXTENSIONS:
        alt = resolved.with_suffix(ext)
        if alt.exists(): return str(alt)
    return None

def _build_semantic_edges(conn):
    conn.execute("DELETE FROM edges WHERE relation IN ('shares_constant','co_occurs')")
    # 共享常量
    edge_counts = {}
    for row in conn.execute("""
        SELECT c1.source_path, c2.source_path, n1.id, n2.id
        FROM constants c1 JOIN constants c2 ON c1.name=c2.name AND c1.source_path<c2.source_path
        JOIN nodes n1 ON n1.path=c1.source_path JOIN nodes n2 ON n2.path=c2.source_path
    """).fetchall():
        k = (min(row[2],row[3]), max(row[2],row[3]))
        edge_counts[k] = edge_counts.get(k,0) + 1
    for (a,b),c in sorted(edge_counts.items(), key=lambda x:-x[1])[:500]:
        conn.execute("INSERT OR IGNORE INTO edges(from_node,to_node,relation,note) VALUES(?,?,?,?)",
                     (a,b,'shares_constant',f'共享 {c} 个常量'))
    # 术语共现
    node_terms = {}
    for nid,cp in conn.execute("SELECT id, content_preview FROM nodes WHERE content_preview IS NOT NULL").fetchall():
        terms = {t for t in KEY_TERMS if t.lower() in (cp or '').lower()}
        if terms: node_terms[nid] = terms
    co = {}
    ids = list(node_terms.keys())
    for i in range(len(ids)):
        for j in range(i+1,len(ids)):
            s = node_terms[ids[i]] & node_terms[ids[j]]
            if len(s) >= 3: co[(min(ids[i],ids[j]),max(ids[i],ids[j]))] = s
    for (a,b),s in sorted(co.items(), key=lambda x:-len(x[1]))[:500]:
        conn.execute("INSERT OR IGNORE INTO edges(from_node,to_node,relation,note) VALUES(?,?,?,?)",
                     (a,b,'co_occurs',f'共现: {", ".join(sorted(s)[:5])}'))

def sync(conn):
    now = datetime.now().isoformat()
    indexed = {r[0]:(r[1],r[2]) for r in conn.execute("SELECT path,mtime,hash FROM files").fetchall()}
    new_f, upd_f = [], []
    for src in SOURCE_DIRS:
        d = Path(src)
        if not d.exists(): continue
        for f in d.rglob("*"):
            if f.suffix.lower() in EXTENSIONS and f.is_file():
                ps = str(f); mt = f.stat().st_mtime; h = hashlib.md5(f.read_bytes()).hexdigest()
                if ps not in indexed: new_f.append((ps,f,mt,h))
                elif indexed[ps][0] < mt or indexed[ps][1] != h: upd_f.append((ps,f,mt,h))
    total = len(new_f) + len(upd_f)
    if total == 0: print("无变更"); return
    existing = dict(conn.execute("SELECT path,id FROM nodes").fetchall())
    cn = 0
    for ps,f,mt,h in new_f + upd_f:
        try: content = f.read_text(errors='ignore')[:50000]
        except: continue
        data = parse_document(f, content)
        pole = classify_pole(ps, data['title'], content)
        sd = str(f.parent); cp = content[:2000]
        if ps in existing:
            conn.execute("UPDATE nodes SET title=?,source_dir=?,pole=?,content_preview=?,summary=? WHERE path=?",
                         (data['title'],sd,pole,cp,data['summary'],ps))
            nid = existing[ps]
            conn.execute("DELETE FROM edges WHERE from_node=?",(nid,))
            conn.execute("DELETE FROM sections WHERE node_id=?",(nid,))
            conn.execute("DELETE FROM constants WHERE source_path=?",(ps,))
        else:
            cur = conn.execute("INSERT INTO nodes(title,path,source_dir,pole,content_preview,summary) VALUES(?,?,?,?,?,?)",
                               (data['title'],ps,sd,pole,cp,data['summary']))
            nid = cur.lastrowid; existing[ps] = nid; cn += 1
        for h,lv in data['sections']:
            conn.execute("INSERT INTO sections(node_id,heading,level,content_preview) VALUES(?,?,?,?)",(nid,h,lv,''))
        for name,val,meaning in data['constants']:
            conn.execute("INSERT OR IGNORE INTO constants(name,value,physical_meaning,source_path) VALUES(?,?,?,?)",(name,val,meaning,ps))
        cd = f.parent
        for lt,ll in data['links']:
            r = resolve_link(ll, cd)
            if r and r in existing:
                tid = existing[r]
                if tid != nid:
                    rel = 'references'
                    tl = (lt + data['title']).lower()
                    if any(k in tl for k in ['验证','实证','valid','实验']): rel = 'validates'
                    elif any(k in tl for k in ['实现','implement','代码']): rel = 'implements'
                    elif any(k in tl for k in ['依赖','depends']): rel = 'depends_on'
                    elif any(k in tl for k in ['推广','泛化','general']): rel = 'generalizes'
                    conn.execute("INSERT OR IGNORE INTO edges(from_node,to_node,relation,note) VALUES(?,?,?,?)",(nid,tid,rel,lt))
        conn.execute("INSERT OR REPLACE INTO files(path,mtime,hash,indexed_at) VALUES(?,?,?,?)",(ps,mt,h,now))
    _build_semantic_edges(conn)
    conn.commit()
    s = _stats(conn)
    print(f"同步: +{cn} 新 | ~{len(upd_f)} 更新 | 总计 {s['nodes']} 节点 {s['edges']} 边 {s['constants']} 常量")

def _stats(conn):
    return {'nodes':conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0],
            'edges':conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0],
            'constants':conn.execute("SELECT COUNT(*) FROM constants").fetchone()[0],
            'sections':conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0],
            'poles':dict(conn.execute("SELECT pole,COUNT(*) FROM nodes GROUP BY pole").fetchall())}

def search(conn, text, limit=8):
    safe = re.sub(r'[\(\)\[\]\{\}"\'\*\^]', '', text).strip()
    if not safe: return []
    return conn.execute(
        "SELECT n.id,n.title,n.pole,n.path,snippet(nodes_fts,2,'<b>','</b>','...',30) FROM nodes_fts f JOIN nodes n ON f.rowid=n.id WHERE nodes_fts MATCH ? ORDER BY rank LIMIT ?",
        (safe, limit)).fetchall()

def query_constants(conn, pattern=None):
    if pattern:
        return conn.execute("SELECT name,value,physical_meaning,source_path FROM constants WHERE name LIKE ? OR value LIKE ?",(f'%{pattern}%',f'%{pattern}%')).fetchall()
    return conn.execute("SELECT DISTINCT name,value,physical_meaning FROM constants ORDER BY name").fetchall()

def query_graph(conn, node_title):
    nodes = conn.execute("SELECT id,title FROM nodes WHERE title LIKE ?",(f'%{node_title}%',)).fetchall()
    if not nodes: return [],[]
    nid = nodes[0][0]
    out = conn.execute("SELECT e.relation,n.title,e.note FROM edges e JOIN nodes n ON e.to_node=n.id WHERE e.from_node=?",(nid,)).fetchall()
    inc = conn.execute("SELECT e.relation,n.title,e.note FROM edges e JOIN nodes n ON e.from_node=n.id WHERE e.to_node=?",(nid,)).fetchall()
    return out, inc

if __name__ == '__main__':
    import sys
    conn = init_db()
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'sync'
    if cmd in ('sync','rebuild'):
        print(f"扫描 {len(SOURCE_DIRS)} 个目录...")
        sync(conn)
    elif cmd == 'search':
        q = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ''
        if q:
            for row in search(conn, q):
                print(f"\n[{row[2]}] {row[1]}\n  {row[3]}\n  {row[4]}")
    elif cmd == 'const':
        p = sys.argv[2] if len(sys.argv) > 2 else None
        for row in query_constants(conn, p):
            print(f"  {row[0]:25s} = {row[1]:15s}  {row[2]}")
    elif cmd == 'graph':
        if len(sys.argv) > 2:
            out, inc = query_graph(conn, sys.argv[2])
            print(f"出边 ({len(out)}):")
            for r,t,n in out: print(f"  → [{r}] {t}")
            print(f"入边 ({len(inc)}):")
            for r,t,n in inc: print(f"  ← [{r}] {t}")
    elif cmd == 'stats':
        s = _stats(conn)
        print(f"节点:{s['nodes']} 边:{s['edges']} 常量:{s['constants']} 小节:{s['sections']}")
        print(f"分类: {s['poles']}")
    elif cmd == 'export':
        nodes = []
        for row in conn.execute("SELECT id,title,pole,summary,path FROM nodes").fetchall():
            out_e = conn.execute("SELECT relation,n.title FROM edges e JOIN nodes n ON e.to_node=n.id WHERE e.from_node=?",(row[0],)).fetchall()
            nodes.append({'title':row[1],'pole':row[2],'summary':row[3],'edges':[{'rel':r,'target':t} for r,t in out_e]})
        print(json.dumps({'nodes':nodes,'constants':[{'name':r[0],'value':r[1],'meaning':r[2]} for r in query_constants(conn)]}, ensure_ascii=False, indent=2))
    conn.close()
