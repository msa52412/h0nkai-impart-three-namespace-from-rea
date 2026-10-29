#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serve_src.py — 还原源码树的本地浏览器

为什么需要它：单个命名空间文件能到 21 MB（MoleMole.cs），直接丢给浏览器会卡死。
所以服务端按类型行号切片，前端只请求当前要看的那一个类型。

用法：
  python serve_src.py [--dir src] [--port 8765]

接口：
  GET /                    单页应用
  GET /api/index           类型级索引（6 MB，前端缓存）
  GET /api/type?i=N        第 N 个类型的源码切片
  GET /api/stats           全局统计
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")

_cache = {}


def load_index():
    if "idx" not in _cache:
        with open(os.path.join(SRC, "_index.json"), encoding="utf-8") as f:
            _cache["idx"] = json.load(f)
        # 按文件把类型行号排序，便于切片时定位
        _cache["lines"] = {}
    return _cache["idx"]


def file_lines(fn):
    if fn not in _cache["lines"]:
        p = os.path.join(SRC, fn)
        with open(p, encoding="utf-8", errors="replace") as f:
            _cache["lines"][fn] = f.read().split("\n")
    return _cache["lines"][fn]


PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>崩坏3 还原源码浏览器</title>
<style>
  :root{
    --bg:#ffffff; --bg2:#f6f7f9; --bd:#e3e6ea; --fg:#1f2328; --dim:#6b7280;
    --accent:#2563eb; --kw:#a626a4; --ty:#c18401; --st:#50a14f; --cm:#9aa0a6; --num:#986801;
  }
  @media (prefers-color-scheme: dark){
    :root{ --bg:#16181d; --bg2:#1d2026; --bd:#2b3038; --fg:#d7dae0; --dim:#8b93a1;
           --accent:#6ea8fe; --kw:#c678dd; --ty:#e5c07b; --st:#98c379; --cm:#6b7280; --num:#d19a66; }
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);
    font:13px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}
  #wrap{display:flex;height:100%}
  #side{width:330px;min-width:330px;border-right:1px solid var(--bd);display:flex;flex-direction:column;background:var(--bg2)}
  #head{padding:10px 12px;border-bottom:1px solid var(--bd)}
  #head h1{font-size:13px;margin:0 0 8px;font-weight:600}
  #head .meta{color:var(--dim);font-size:11px;margin-top:6px}
  input{width:100%;padding:7px 9px;border:1px solid var(--bd);border-radius:6px;
    background:var(--bg);color:var(--fg);font-size:12px;outline:none}
  input:focus{border-color:var(--accent)}
  #list{flex:1;overflow:auto}
  .item{padding:6px 12px;border-bottom:1px solid var(--bd);cursor:pointer}
  .item:hover{background:rgba(127,127,127,.10)}
  .item.on{background:rgba(37,99,235,.16)}
  .item .n{font-weight:600}
  .item .s{color:var(--dim);font-size:11px;margin-top:1px}
  .badge{display:inline-block;padding:0 5px;border-radius:4px;background:rgba(127,127,127,.16);
    font-size:10px;margin-right:4px;color:var(--dim)}
  .nest{color:var(--dim);margin-right:3px;font-size:11px}
  #bar .pl{color:var(--accent);text-decoration:none}
  #bar .pl:hover{text-decoration:underline}
  #main{flex:1;display:flex;flex-direction:column;overflow:hidden}
  #bar{padding:8px 14px;border-bottom:1px solid var(--bd);display:flex;gap:12px;
    align-items:center;font-size:12px;color:var(--dim);flex-wrap:wrap}
  #bar b{color:var(--fg)}
  #code{flex:1;overflow:auto;padding:8px 0}
  pre{margin:0;font:12px/1.5 "Cascadia Mono",Consolas,"Courier New",monospace;
    tab-size:4;white-space:pre}
  .ln{display:flex}
  .ln .g{width:56px;min-width:56px;text-align:right;padding-right:12px;color:var(--dim);
    user-select:none;font-size:11px}
  .ln .t{flex:1;white-space:pre}
  .kw{color:var(--kw)} .ty{color:var(--ty)} .st{color:var(--st)}
  .cm{color:var(--cm);font-style:italic} .nu{color:var(--num)}
  .va{color:var(--accent)}
  #empty{padding:40px;color:var(--dim);text-align:center}
  .hint{color:var(--dim);font-size:11px;padding:8px 12px}
</style>
</head>
<body>
<div id="wrap">
  <div id="side">
    <div id="head">
      <h1>崩坏3 还原源码浏览器</h1>
      <input id="q" placeholder="搜索类型名 / 命名空间 …  (按 / 聚焦)">
      <div class="meta" id="meta">载入中 …</div>
    </div>
    <div id="list"></div>
  </div>
  <div id="main">
    <div id="bar"><span id="cur">从左侧选一个类型</span></div>
    <div id="code"><div id="empty">← 左侧搜索或浏览</div></div>
  </div>
</div>
<script>
let IDX=null, TYPES=[], cur=-1, shown=[];
const q=document.getElementById('q'), list=document.getElementById('list'),
      code=document.getElementById('code'), bar=document.getElementById('cur'),
      meta=document.getElementById('meta');

function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}

const KW=new Set(('abstract as base bool break byte case catch char checked class const continue '+
 'decimal default delegate do double else enum event explicit extern false finally fixed float for '+
 'foreach goto if implicit in int interface internal is lock long namespace new null object operator '+
 'out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc '+
 'static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using '+
 'virtual void volatile while var get set value').split(' '));

function hi(line){
  // 单行高亮：注释 > 字符串 > 关键字/类型/数字
  const out=[]; let i=0;
  while(i<line.length){
    const rest=line.slice(i);
    if(rest.startsWith('//')){ out.push('<span class="cm">'+esc(rest)+'</span>'); break; }
    if(rest.startsWith('/*')){ const e=line.indexOf('*/',i+2); const j=e<0?line.length:e+2;
      out.push('<span class="cm">'+esc(line.slice(i,j))+'</span>'); i=j; continue; }
    const c=line[i];
    if(c==='"'||c==="'"){ let j=i+1; while(j<line.length){ if(line[j]==='\\'){j+=2;continue;}
      if(line[j]===c){j++;break;} j++; }
      out.push('<span class="st">'+esc(line.slice(i,j))+'</span>'); i=j; continue; }
    if(/[A-Za-z_$]/.test(c)){ let j=i+1; while(j<line.length && /[A-Za-z0-9_$]/.test(line[j])) j++;
      const w=line.slice(i,j);
      if(KW.has(w)) out.push('<span class="kw">'+esc(w)+'</span>');
      else if(/^[A-Z]/.test(w)) out.push('<span class="ty">'+esc(w)+'</span>');
      else out.push(esc(w));
      i=j; continue; }
    if(/[0-9]/.test(c)){ let j=i+1; while(j<line.length && /[0-9a-fA-FxX._]/.test(line[j])) j++;
      out.push('<span class="nu">'+esc(line.slice(i,j))+'</span>'); i=j; continue; }
    out.push(esc(c)); i++;
  }
  return out.join('');
}

function parentOf(t){ const p=t[11]; return (p>=0 && TYPES[p]) ? TYPES[p] : null; }
function fullName(t){ const p=parentOf(t); return p ? (p[1]+'.'+t[1]) : t[1]; }

function render(list, n){
  if(!n){ list.innerHTML='<div id="empty">没有匹配</div>'; return; }
  const cap=Math.min(n,400);
  const buf=[];
  for(let k=0;k<cap;k++){
    const i=shown[k], t=TYPES[i], p=parentOf(t);
    buf.push('<div class="item'+(i===cur?' on':'')+'" data-i="'+i+'">'+
      '<div class="n"><span class="badge">'+esc(t[3])+'</span>'+
      (p?'<span class="nest">⊂</span>':'')+esc(fullName(t))+'</div>'+
      '<div class="s">'+esc(p?('嵌套于 '+p[1]):(t[0]||'&lt;全局&gt;'))+' · '+t[7]+' 方法 · 0x'+(t[9]||0).toString(16).toUpperCase()+'</div></div>');
  }
  if(n>cap) buf.push('<div class="hint">还有 '+(n-cap)+' 条，请输入更精确的关键词</div>');
  list.innerHTML=buf.join('');
  [...list.querySelectorAll('.item')].forEach(el=>{
    el.onclick=()=>open_(+el.dataset.i);
  });
}

function filter(){
  const k=q.value.trim().toLowerCase();
  if(!k){ shown=[]; for(let i=0;i<TYPES.length && i<400;i++) shown.push(i); render(list,Math.min(TYPES.length,400)); return; }
  const parts=k.split(/\s+/); shown=[];
  for(let i=0;i<TYPES.length;i++){
    const t=TYPES[i];
    const p=parentOf(t);
    const hay=(t[1]+' '+(t[0]||'')+(p?' '+p[1]:'')).toLowerCase();
    let ok=true;
    for(const p of parts){ if(hay.indexOf(p)<0){ok=false;break;} }
    if(ok){ shown.push(i); if(shown.length>=2000) break; }
  }
  render(list,shown.length);
}

async function open_(i){
  cur=i; const t=TYPES[i], p=parentOf(t);
  [...list.querySelectorAll('.item')].forEach(el=>el.classList.toggle('on',+el.dataset.i===i));
  bar.innerHTML='<b>'+esc(fullName(t))+'</b> <span>'+esc(t[0]||'&lt;全局&gt;')+'</span> '+
    (p?'<span>嵌套于 <a href="#" class="pl" data-p="'+t[11]+'">'+esc(p[1])+'</a></span> ':'')+
    '<span>'+t[7]+' 个方法</span> <span>'+esc(t[8])+'</span> '+
    (t[9]?'<span>0x'+t[9].toString(16).toUpperCase()+' 字节</span>':'')+
    (t[10]?'<span>布局 '+esc(t[10])+'</span>':'');
  const pl=bar.querySelector('.pl');
  if(pl) pl.onclick=ev=>{ ev.preventDefault(); open_(+pl.dataset.p); };
  code.innerHTML='<div id="empty">载入中 …</div>';
  const r=await fetch('/api/type?i='+i); const txt=await r.text();
  const lines=txt.split('\n'); const buf=[];
  const base=t[5];
  for(let k=0;k<lines.length;k++){
    buf.push('<div class="ln"><span class="g">'+(base+k)+'</span><span class="t">'+hi(lines[k])+'</span></div>');
  }
  code.innerHTML='<pre>'+buf.join('')+'</pre>';
  code.scrollTop=0;
}

q.addEventListener('input',filter);
document.addEventListener('keydown',e=>{
  if(e.key==='/'){ q.focus(); e.preventDefault(); }
  else if(e.key==='Enter' && document.activeElement===q && shown.length){ open_(shown[0]); }
});

(async()=>{
  const r=await fetch('/api/index'); IDX=await r.json(); TYPES=IDX.types;
  const nsN=Object.keys(IDX.namespaces).length;
  let meth=0, body=0;
  meta.textContent=TYPES.length.toLocaleString()+' 个类型 · '+nsN+' 个命名空间'+
    (IDX.nested?' · '+IDX.nested.toLocaleString()+' 个嵌套类型已归位':'');
  filter();
})();
</script>
</body>
</html>
"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if u.path == "/api/index":
            try:
                idx = load_index()
            except Exception as e:
                return self._send(500, json.dumps({"error": str(e)}))
            return self._send(200, json.dumps(idx, ensure_ascii=False,
                                             separators=(",", ":")))
        if u.path == "/api/type":
            try:
                i = int(parse_qs(u.query).get("i", ["0"])[0])
                idx = load_index()
                t = idx["types"][i]
                fn, start, n = t[4], t[5], t[6]
                lines = file_lines(fn)
                seg = lines[start - 1:start - 1 + n]
                return self._send(200, "\n".join(seg), "text/plain; charset=utf-8")
            except Exception as e:
                return self._send(500, json.dumps({"error": str(e)}))
        if u.path == "/api/stats":
            idx = load_index()
            return self._send(200, json.dumps({
                "types": len(idx["types"]),
                "namespaces": len(idx["namespaces"]),
            }, ensure_ascii=False))
        return self._send(404, "not found", "text/plain; charset=utf-8")


def main():
    global SRC
    port = 8765
    a = sys.argv[1:]
    i = 0
    while i < len(a):
        if a[i] == "--dir":
            SRC = os.path.abspath(a[i + 1]); i += 2
        elif a[i] == "--port":
            port = int(a[i + 1]); i += 2
        else:
            i += 1
    if not os.path.exists(os.path.join(SRC, "_index.json")):
        print("找不到 %s/_index.json，请先跑 gen_cs.py" % SRC)
        return
    load_index()
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print("源码浏览器: http://127.0.0.1:%d/  (目录 %s)" % (port, SRC))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
