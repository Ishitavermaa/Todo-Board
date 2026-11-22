"""Minimal to-do board. Run: python todo_board.py  (no installs needed)
Opens in your browser at http://localhost:8000. Tasks are saved in tasks.json.
"""
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "tasks.json")
PORT = 8000

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tasks</title>
<style>
:root{--bg:#fff;--ink:#1c1c1e;--mute:#8a8a8e;--line:#ececee;--red:#d6336c;--amber:#b7791f;--accent:#1c1c1e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:40px 28px}
header{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}
h1{font-size:22px;font-weight:600;margin:0;letter-spacing:-.01em}
.stats{color:var(--mute);font-size:14px}
.stats b{color:var(--ink);font-weight:500}
.bar{display:flex;gap:10px;align-items:center;margin:28px 0 32px;flex-wrap:wrap}
.bar input,.bar select{font:inherit;color:var(--ink);background:none;border:0;border-bottom:1px solid var(--line);padding:6px 2px;outline:none;border-radius:0}
.bar input:focus,.bar select:focus{border-color:var(--ink)}
.seg{display:flex;gap:14px;margin-right:6px}
.seg button{font:inherit;background:none;border:0;padding:6px 0;color:var(--mute);cursor:pointer;border-bottom:1px solid transparent}
.seg button.on{color:var(--ink);border-color:var(--ink)}
.sp{flex:1}
.add{font:inherit;background:var(--accent);color:#fff;border:0;border-radius:6px;padding:8px 14px;cursor:pointer}
.board{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:36px;align-items:start}
.col h2{font-size:14px;font-weight:500;margin:0 0 6px;display:flex;align-items:center;gap:8px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.dot{width:8px;height:8px;border-radius:50%}
.n{color:var(--mute);font-weight:400}
.task{padding:14px 0;border-bottom:1px solid var(--line);display:flex;gap:10px;position:relative}
.task input[type=checkbox]{margin:4px 0 0;accent-color:var(--ink);width:15px;height:15px;flex:none;cursor:pointer}
.t{font-weight:500}
.d{color:var(--mute);font-size:13.5px;margin-top:2px;white-space:pre-wrap}
.due{font-size:13px;margin-top:6px;color:var(--mute)}
.due.over{color:var(--red)}.due.today{color:var(--amber)}
.task.done .t{text-decoration:line-through;color:var(--mute);font-weight:400}
.task.done .due{color:var(--mute)}
.x{position:absolute;right:0;top:12px;background:none;border:0;color:var(--mute);font-size:18px;cursor:pointer;opacity:0;line-height:1}
.task:hover .x,.x:focus{opacity:1}
.empty{color:var(--mute);padding:60px 0;text-align:center}
dialog{border:1px solid var(--line);border-radius:10px;padding:24px;width:min(420px,92vw);box-shadow:0 10px 40px rgba(0,0,0,.12)}
dialog::backdrop{background:rgba(255,255,255,.7)}
dialog h3{margin:0 0 16px;font-size:17px;font-weight:600}
label{display:block;font-size:13px;color:var(--mute);margin:12px 0 2px}
dialog input,dialog textarea{width:100%;font:inherit;border:0;border-bottom:1px solid var(--line);padding:6px 0;outline:none;background:none;color:var(--ink);resize:vertical}
dialog input:focus,dialog textarea:focus{border-color:var(--ink)}
.row{display:flex;gap:16px}.row>div{flex:1}
.acts{display:flex;justify-content:flex-end;gap:10px;margin-top:22px}
.acts button{font:inherit;border-radius:6px;padding:8px 14px;cursor:pointer;border:1px solid var(--line);background:none;color:var(--ink)}
.acts .go{background:var(--accent);color:#fff;border-color:var(--accent)}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
</style></head><body><main>
<header><h1>Tasks</h1><div class="stats" id="stats"></div></header>
<div class="bar">
  <div class="seg" id="seg"><button data-f="all" class="on">All</button><button data-f="active">Active</button><button data-f="done">Completed</button></div>
  <select id="cat"></select>
  <input id="q" placeholder="Search" aria-label="Search tasks">
  <span class="sp"></span>
  <select id="sort"><option value="due">Earliest deadline</option><option value="new">Newest first</option><option value="az">A to Z</option></select>
  <button class="add" id="open">New task</button>
</div>
<div class="board" id="board"></div>

<dialog id="dlg"><form method="dialog" id="f" style="margin:0">
  <h3>New task</h3>
  <label for="ti">Heading</label><input id="ti" required>
  <div class="row"><div><label for="da">Due date</label><input id="da" type="date" required></div>
  <div><label for="tm">Time (optional)</label><input id="tm" type="time"></div></div>
  <label for="ca">Category</label><input id="ca" list="cats" required placeholder="e.g. Deep Work"><datalist id="cats"></datalist>
  <label for="de">Description</label><textarea id="de" rows="3"></textarea>
  <div class="acts"><button type="button" id="cancel">Cancel</button><button class="go" type="submit">Add task</button></div>
</form></dialog>
</main>
<script>
let tasks=[],filter="all";
const $=id=>document.getElementById(id);
const PAL=["#e5484d","#d9774f","#6366f1","#2fa77a","#c08a1e","#3b82c4","#a855a8","#6b7280"];
const color=c=>{let h=0;for(const ch of c)h=(h*31+ch.charCodeAt(0))>>>0;return PAL[h%PAL.length]};
const esc=s=>s.replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
const dueDate=t=>new Date(t.time?`${t.date}T${t.time}`:`${t.date}T23:59`);
const sameDay=(a,b)=>a.toDateString()===b.toDateString();
function fmt(t){
  const d=dueDate(t),now=new Date(),tm=t.time?d.toLocaleTimeString([], {hour:"numeric",minute:"2-digit"}):"";
  const day=sameDay(d,now)?"Today":d.toLocaleDateString([], {month:"short",day:"numeric"});
  return tm?`${day}, ${tm}`:day;
}
async function load(){tasks=await (await fetch("/api/tasks")).json();render()}
function save(){fetch("/api/tasks",{method:"POST",body:JSON.stringify(tasks)})}
function render(){
  const now=new Date(),q=$("q").value.toLowerCase(),cat=$("cat").value||"all";
  const cats=[...new Set(tasks.map(t=>t.category))].sort();
  $("cat").innerHTML=`<option value="all">All categories (${cats.length})</option>`+cats.map(c=>`<option ${c===cat?"selected":""}>${esc(c)}</option>`).join("");
  $("cats").innerHTML=cats.map(c=>`<option value="${esc(c)}">`).join("");
  const open=tasks.filter(t=>!t.done);
  const today=open.filter(t=>sameDay(dueDate(t),now)).length;
  const over=open.filter(t=>dueDate(t)<now&&!sameDay(dueDate(t),now)||(t.time&&dueDate(t)<now)).length;
  $("stats").innerHTML=`<b>${tasks.length}</b> total &nbsp; <b>${today}</b> due today &nbsp; <b>${over}</b> overdue &nbsp; <b>${tasks.length-open.length}</b> done`;
  let list=tasks.filter(t=>(filter==="all"||(filter==="done")===t.done)&&(cat==="all"||t.category===cat)&&(t.title+t.description).toLowerCase().includes(q));
  const s=$("sort").value;
  list.sort((a,b)=>s==="az"?a.title.localeCompare(b.title):s==="new"?b.id-a.id:dueDate(a)-dueDate(b));
  const groups={};list.forEach(t=>(groups[t.category]??=[]).push(t));
  const names=Object.keys(groups).sort();
  $("board").innerHTML=names.length?names.map(c=>`<section class="col"><h2><span class="dot" style="background:${color(c)}"></span>${esc(c)} <span class="n">${groups[c].length}</span></h2>`+
    groups[c].map(t=>{
      const d=dueDate(t),cls=t.done?"":(d<now?"over":sameDay(d,now)?"today":"");
      return `<article class="task ${t.done?"done":""}"><input type="checkbox" ${t.done?"checked":""} data-id="${t.id}" aria-label="Mark done">
      <div><div class="t">${esc(t.title)}</div>${t.description?`<div class="d">${esc(t.description)}</div>`:""}<div class="due ${cls}">${fmt(t)}</div></div>
      <button class="x" data-del="${t.id}" aria-label="Delete task">&times;</button></article>`}).join("")+`</section>`).join(""):`<div class="empty">No tasks here. Add one with “New task”.</div>`;
}
$("board").addEventListener("click",e=>{
  const id=e.target.dataset.id,del=e.target.dataset.del;
  if(id){const t=tasks.find(x=>x.id==id);t.done=e.target.checked;save();render()}
  if(del&&confirm("Delete this task?")){tasks=tasks.filter(x=>x.id!=del);save();render()}
});
$("seg").addEventListener("click",e=>{if(!e.target.dataset.f)return;filter=e.target.dataset.f;
  document.querySelectorAll("#seg button").forEach(b=>b.classList.toggle("on",b===e.target));render()});
["q","cat","sort"].forEach(i=>$(i).addEventListener("input",render));
$("open").onclick=()=>{$("f").reset();$("da").value=new Date().toLocaleDateString("en-CA");$("dlg").showModal();$("ti").focus()};
$("cancel").onclick=()=>$("dlg").close();
$("f").addEventListener("submit",()=>{
  tasks.push({id:Date.now(),title:$("ti").value.trim(),date:$("da").value,time:$("tm").value,category:$("ca").value.trim(),description:$("de").value.trim(),done:false});
  save();render();
});
load();
</script></body></html>"""


def read_tasks():
    try:
        with open(DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/tasks":
            self._send(json.dumps(read_tasks()).encode(), "application/json")
        else:
            self._send(PAGE.encode("utf-8"), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path == "/api/tasks":
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"[]")
            with open(DATA, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        self._send(b"ok", "text/plain")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"To-do board running at {url}  (Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
