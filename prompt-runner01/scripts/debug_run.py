from api import run_prompt, RunRequest
from fastapi import HTTPException
import json

req = RunRequest(prompt='what is software')
try:
    out = run_prompt(req)
    print('CALL OK:', json.dumps(out)[:2000])
except HTTPException as e:
    print('HTTPException status', e.status_code, e.detail)
except Exception as e:
    print('EXC', repr(e))
