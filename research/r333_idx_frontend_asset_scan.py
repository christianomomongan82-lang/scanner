#!/usr/bin/env python3
"""Fetch official IDX page assets referenced by already-acquired IDX HTML and scan routes; no market/PnL calculations."""
from __future__ import annotations
import hashlib,json,os,re,time
from datetime import datetime,timezone
from pathlib import Path
import requests

ROOT=Path(os.environ["R333_DATA_ROOT"]).resolve()
ASSETS=ROOT/"data"/"r333"/"idx_metadata"/"frontend_assets"
MANIFEST=ROOT/"data"/"r333"/"manifests"
INPUTS=[
 "data/r333/idx_metadata/listing_activity_block_page.html",
 "data/r333/idx_metadata/stock_list_page.html",
]
HEADERS={
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
 "Accept":"application/javascript,*/*;q=0.8",
 "Referer":"https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan",
}
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 ASSETS.mkdir(parents=True,exist_ok=True); MANIFEST.mkdir(parents=True,exist_ok=True)
 session=requests.Session();session.headers.update(HEADERS)
 pages=[]
 for rel in INPUTS:
  p=ROOT/rel
  if p.exists(): pages.append((rel,p.read_text(encoding="utf-8",errors="replace")))
 if not pages: raise SystemExit("INPUT_HTML_MISSING: official IDX page snapshots are not present on data branch.")
 paths=[]
 for source,html in pages:
  for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',html,re.I):
   if src.startswith("/_nuxt/") and src.endswith(".js"):
    if src not in paths: paths.append(src)
 print(f"IDX_FRONTEND_ASSETS discovered_unique_js={len(paths)} from_pages={[x[0] for x in pages]}")
 assets=[]; route_hits=set(); delist_hits=set()
 for idx,path in enumerate(paths,1):
  url="https://block.idx.id"+path if path.startswith("/") else path
  entry={"path":path,"url":url,"started_utc":now(),"status":"FAILED"}
  try:
   response=session.get(url,timeout=40,allow_redirects=True)
   body=response.content
   entry.update({"http_status":response.status_code,"final_url":response.url,"content_type":response.headers.get("Content-Type",""),"bytes":len(body)})
   print(f"IDX_JS name={path} status={response.status_code} bytes={len(body)}")
   if response.status_code==200 and len(body)>100:
    out=ASSETS/(Path(path).name)
    out.write_bytes(body)
    entry.update({"status":"FETCHED","saved_path":str(out.relative_to(ROOT)),"sha256":sha(body)})
    text=body.decode("utf-8",errors="replace")
    # URLs/routes referenced by the official app; preserve only route snippets, not arbitrary user/secret values.
    for match in re.finditer(r'(?:(?:https?:\\/\\/[^"\'\\s]{0,180})|(?:/(?:primary|umbraco/Surface|api)/[^"\'\\s]{1,180}))',text,re.I):
     raw=match.group(0).replace("\\/", "/")
     if any(tok in raw.lower() for tok in ["primary/","umbraco/surface/","/api/"]):
      route_hits.add(raw[:240])
    for match in re.finditer(r'.{0,100}(?:delist|listingactivit|stockdata|getsecur|listedcompany).{0,180}',text,re.I):
     snippet=re.sub(r"\\s+"," ",match.group(0))
     if re.search(r"delist|listingactivit",snippet,re.I):
      delist_hits.add(snippet[:320])
  except Exception as exc:
   entry.update({"error_type":type(exc).__name__,"error_message":str(exc)})
   print(f"IDX_JS_ERROR path={path} error_type={type(exc).__name__} error={str(exc)!r}")
  entry["finished_utc"]=now();assets.append(entry)
 result={
  "experiment":"R333","purpose":"official IDX frontend asset inspection for documented public endpoints only; no signals/PnL",
  "run_id":os.getenv("GITHUB_RUN_ID","local"),"run_attempt":os.getenv("GITHUB_RUN_ATTEMPT","1"),
  "started_utc":assets[0]["started_utc"] if assets else now(),"finished_utc":now(),
  "input_pages":[{"path":rel,"sha256":sha((ROOT/rel).read_bytes())} for rel,_ in pages],
  "asset_count":len(assets),"assets":assets,"route_hits":sorted(route_hits),"delisting_related_snippets":sorted(delist_hits),
  "note":"A discovered endpoint is not treated as reliable until a separate request in an acquisition-only workflow succeeds and its raw response is committed."
 }
 p=MANIFEST/"idx-frontend-assets-latest.json"
 p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
 print(f"IDX_ASSET_SCAN_STATUS={'COMPLETE' if assets and any(x['status']=='FETCHED' for x in assets) else 'NO_ASSETS'}")
 with open(os.getenv("GITHUB_OUTPUT","/dev/null"),"a",encoding="utf-8") as f:
  f.write(f"asset_status={'COMPLETE' if assets and any(x['status']=='FETCHED' for x in assets) else 'NO_ASSETS'}\\n")
 return 0 if assets and any(x["status"]=="FETCHED" for x in assets) else 1
if __name__=="__main__": raise SystemExit(main())
