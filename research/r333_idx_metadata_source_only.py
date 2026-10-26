#!/usr/bin/env python3
"""R333 official IDX listing metadata acquisition only. Never calculates signals or PnL."""
from __future__ import annotations
import hashlib, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

DATA_ROOT=Path(os.environ["R333_DATA_ROOT"]).resolve()
RUN_ID=os.getenv("GITHUB_RUN_ID","local")
RUN_ATTEMPT=os.getenv("GITHUB_RUN_ATTEMPT","1")
OUT=DATA_ROOT/"data"/"r333"/"idx_metadata"
MANIFEST=DATA_ROOT/"data"/"r333"/"manifests"

HEADERS={
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
 "Accept":"application/json, text/html, */*",
 "Accept-Language":"id-ID,id;q=0.9,en;q=0.8",
 "Referer":"https://www.idx.co.id/id/data-pasar/data-saham/daftar-saham",
}

# Only official IDX domains are used. Routes are recorded separately; failure is not silently replaced with another provider.
SOURCES=[
 ("listed_securities_primary","https://www.idx.co.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000","json"),
 ("listed_securities_umbraco","https://www.idx.co.id/umbraco/Surface/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000","json"),
 ("listed_securities_block","https://block.idx.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000","json"),
 ("listing_activity_page","https://www.idx.co.id/id/perusahaan-tercatat/aktivitas-pencatatan","html"),
 ("listing_activity_block_page","https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan","html"),
 ("stock_list_page","https://block.idx.id/id/data-pasar/data-saham/daftar-saham/","html"),
]
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def sha(raw: bytes): return hashlib.sha256(raw).hexdigest()
def write_json(p:Path,obj:Any):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def find_record_arrays(obj:Any):
 found=[]
 def walk(x):
  if isinstance(x,dict):
   # candidate if any dict values resemble stock list fields
   vals={str(k).lower() for k in x.keys()}
   score=sum(1 for v in ["stockcode","code","listingdate","listedshares","shares","listingboard","board"] if v in vals)
   if score>=2: found.append(x)
   for v in x.values(): walk(v)
  elif isinstance(x,list):
   for v in x: walk(v)
 walk(obj)
 return found
def main():
 OUT.mkdir(parents=True,exist_ok=True); MANIFEST.mkdir(parents=True,exist_ok=True)
 session=requests.Session(); session.headers.update(HEADERS)
 results=[]; valid_listing=None
 for name,url,kind in SOURCES:
  entry={"name":name,"url":url,"kind":kind,"attempts":[],"status":"FAILED","started_utc":now()}
  for attempt in range(1,4):
   t=now()
   try:
    resp=session.get(url,timeout=35,allow_redirects=True)
    ctype=resp.headers.get("Content-Type","")
    status=resp.status_code
    body=resp.content
    entry["attempts"].append({"attempt":attempt,"started_utc":t,"finished_utc":now(),"http_status":status,"final_url":resp.url,"content_type":ctype,"bytes":len(body),"error":None if status==200 else f"HTTP {status}: {resp.text[:500]}"})
    print(f"IDX_SOURCE name={name} attempt={attempt} status={status} bytes={len(body)} content_type={ctype}")
    if status==200 and len(body)>100:
     suffix=".json" if kind=="json" else ".html"
     path=OUT/f"{name}{suffix}"; path.write_bytes(body)
     entry.update({"status":"FETCHED","saved_path":str(path.relative_to(DATA_ROOT)),"bytes":len(body),"sha256":sha(body),"content_type":ctype,"final_url":resp.url})
     if kind=="json":
      try:
       parsed=resp.json()
       parsed_path=OUT/f"{name}_parsed.json"; write_json(parsed_path,parsed)
       entry["parsed_path"]=str(parsed_path.relative_to(DATA_ROOT))
       entry["parsed_sha256"]=sha(parsed_path.read_bytes())
       arrays=find_record_arrays(parsed)
       if arrays:
        entry["candidate_record_objects"]=len(arrays)
       # Only select a payload with an array/container that clearly declares stock-code fields.
       if name.startswith("listed_securities") and parsed is not None:
        def has_stock_codes(x):
         if isinstance(x,list) and x and all(isinstance(i,dict) for i in x[:10]):
          keys={str(k).lower() for i in x[:10] for k in i.keys()}
          return bool(keys & {"stockcode","code","securitycode"}) and bool(keys & {"listingdate","listedshares","shares"})
         if isinstance(x,dict):
          return any(has_stock_codes(v) for v in x.values())
         return False
        if has_stock_codes(parsed) and valid_listing is None:
         valid_listing={"source":name,"path":str(parsed_path.relative_to(DATA_ROOT)),"url":url}
     except Exception as exc:
      entry["json_parse_error"]=f"{type(exc).__name__}: {exc}"
     break
    else:
     entry["status"]="FAILED"
   except Exception as exc:
    entry["attempts"].append({"attempt":attempt,"started_utc":t,"finished_utc":now(),"http_status":None,"error_type":type(exc).__name__,"error_message":str(exc)})
    print(f"IDX_SOURCE_ERROR name={name} attempt={attempt} error_type={type(exc).__name__} error={str(exc)!r}")
   if attempt < 3:
    delay=[30,120][attempt-1]
    print(f"IDX_SOURCE_RETRY name={name} wait_seconds={delay}")
    time.sleep(delay)
  entry["finished_utc"]=now()
  results.append(entry)
 overall="ROSTER_JSON_FOUND" if valid_listing else "IDX_SOURCE_NOT_VERIFIED"
 manifest={
  "experiment":"R333",
  "purpose":"official IDX listing/delisting metadata source acquisition only; no selection by PnL, no signals or PnL",
  "run_id":RUN_ID,"run_attempt":RUN_ATTEMPT,"started_utc":results[0]["started_utc"] if results else now(),"finished_utc":now(),
  "official_domains_only":True,
  "overall_status":overall,
  "sources":results,
  "selected_roster":valid_listing,
  "limitations":[
   "Current listing metadata alone is not a historical point-in-time universe.",
   "Do not assume complete delisted coverage or historical shares outstanding merely because a current roster was downloaded.",
   "If historical delisted names or point-in-time shares/sectors cannot be established, mark results survivorship-biased/data-inadequate and do not claim an edge without an explicit defensible correction."
  ]
 }
 write_json(MANIFEST/"idx-metadata-latest.json",manifest)
 write_json(MANIFEST/f"idx_metadata_run_{RUN_ID}_attempt_{RUN_ATTEMPT}.json",manifest)
 print(f"IDX_METADATA_STATUS={overall}")
 # Always retain evidence. The workflow job is red if no parseable official current security list was found.
 with open(os.getenv("GITHUB_OUTPUT","/dev/null"),"a",encoding="utf-8") as f:
  f.write(f"roster_status={overall}\n")
 return 0 if valid_listing else 1
if __name__=="__main__": raise SystemExit(main())
