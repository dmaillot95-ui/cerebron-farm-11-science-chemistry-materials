import os,json,pathlib,subprocess
role=os.environ['ROLE']; focus=os.environ['FOCUS']; model=os.environ['MODEL']
prompt=f'''You are role {role} in CEREBRON Farm 11 Science Chemistry Materials. Focus: {focus}. Distinguish ESTABLISHED/DERIVED/CONJECTURAL/SPECULATIVE/UNKNOWN. State assumptions, validation needs, safety limits and failure modes. SIMULATION != TEST. CLAIM <= EVIDENCE.'''
def run(cmd,t=240): return subprocess.run(cmd,capture_output=True,text=True,timeout=t)
def payload(spec,prompt):
 d={}; used=False
 for p in spec.get('parameters',[]):
  n=p.get('name',''); l=n.lower(); req=bool(p.get('required')); default=p.get('default'); typ=(p.get('type') or {}).get('type')
  if l in {'message','prompt','text','query','input','instruction','user_message'}: d[n]=prompt; used=True
  elif l in {'chat_history','history','messages'}: d[n]=[]
  elif l in {'max_new_tokens','max_tokens','maximum_new_tokens'}: d[n]=700
  elif l=='temperature': d[n]=0.1
  elif l=='top_p': d[n]=0.9
  elif req and default is None:
   if typ=='string' and not used: d[n]=prompt; used=True
   else: return None
 return d if used else None
def invoke(space,prompt):
 i=run(['hf-gradio','info',space],120)
 if i.returncode: return False,'',{'stage':'info','error':(i.stderr or i.stdout)[-1200:]}
 try: api=json.loads(i.stdout)
 except Exception as e: return False,'',{'stage':'decode','error':repr(e)}
 pref=['/generate','/chat','/predict','/respond','/infer','/run']; eps=list(api.items()); eps.sort(key=lambda kv:(pref.index(kv[0]) if kv[0] in pref else 99,kv[0]))
 errs=[]
 for ep,spec in eps:
  pl=payload(spec,prompt)
  if pl is None: continue
  r=run(['hf-gradio','predict',space,ep,json.dumps(pl,ensure_ascii=False)],240)
  if r.returncode==0 and (r.stdout or '').strip(): return True,r.stdout.strip(),{'endpoint':ep}
  errs.append((r.stderr or r.stdout)[-700:])
 return False,'',{'stage':'predict','error':' | '.join(errs[-3:])}
ok,text,meta=invoke(model,prompt)
res={'role':role,'model':model,'status':'SUCCESS' if ok else 'EXTERNAL_INFERENCE_FAILED','epistemic_status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'NO_EXTERNAL_OUTPUT','output':text if ok else None,'meta':meta}
pathlib.Path('out').mkdir(exist_ok=True)
pathlib.Path(f'out/{role}.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
