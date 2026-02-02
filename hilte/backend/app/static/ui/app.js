const API='http://127.0.0.1:8008';

export async function fetchJson(path){
  const r = await fetch(API + path, {mode:'cors'});
  const t = await r.text();
  if(!r.ok) throw new Error(`${path} HTTP ${r.status}: ${t.slice(0,200)}`);
  return JSON.parse(t);
}

export function pill(status){
  const s=String(status||'').toLowerCase();
  let cls='';
  if(['paid','done','converted','confirmed'].includes(s)) cls='green';
  else if(['failed','canceled','cancelled','blocked'].includes(s)) cls='red';
  else if(['pending','requested','open','in_progress','qa_hold'].includes(s)) cls='amber';
  return `<span class="pill ${cls}">${status||'—'}</span>`;
}

export function fmtDT(v){
  if(!v) return '—';
  try{return new Date(v).toLocaleString();}catch{return String(v)}
}
