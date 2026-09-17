import os,json,pathlib
from gradio_client import Client
role=os.environ['ROLE']; focus=os.environ['FOCUS']; model=os.environ['MODEL']
prompt=f'''You are role {role} in CEREBRON Farm 11 Science Chemistry Materials. Focus: {focus}. Produce a concise scientific analysis. Distinguish ESTABLISHED/DERIVED/CONJECTURAL/SPECULATIVE. State assumptions, validation needs, safety limits and failure modes. SIMULATION != TEST. CLAIM <= EVIDENCE.'''
res={'role':role,'model':model,'status':'FAILED'}
try:
 c=Client(model)
 out=c.predict(message=prompt,api_name='/chat')
 res['status']='SUCCESS'; res['output']=str(out)
except Exception as e: res['error']=repr(e)
pathlib.Path('out').mkdir(exist_ok=True)
pathlib.Path(f'out/{role}.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
