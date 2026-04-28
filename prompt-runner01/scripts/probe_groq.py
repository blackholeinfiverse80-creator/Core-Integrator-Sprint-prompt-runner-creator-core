import os,requests
# load .env.local if present
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    with open(env_path,'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.split('=',1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
key = os.environ.get('GROQ_API_KEY')
print('GROQ_API_KEY present:', bool(key))
if not key:
    raise SystemExit(0)
url='https://api.groq.com/openai/v1/chat/completions'
headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'}
payload={
 'model':'llama-3.3-70b-versatile',
 'messages':[{'role':'system','content':'ping'},{'role':'user','content':'hello'}],
 'temperature':0,
 'max_tokens':1
}
try:
    r=requests.post(url,headers=headers,json=payload,timeout=10)
    print('STATUS',r.status_code)
    txt = r.text or ''
    print(txt[:800])
except Exception as e:
    print('ERROR',repr(e))
