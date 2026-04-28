import creator_core_client as c
import requests

print('CREATOR_CORE_URL=' + c.CREATOR_CORE_URL)
url = c.CREATOR_CORE_URL
p={'prompt':'x','module':'m','intent':'i','topic':'t','tasks':['a'],'output_format':'md','product_context':'creator_core'}
try:
    r = requests.post(url, json=p, timeout=5)
    print('PROBE_CONFIGURED_URL', url, 'STATUS', r.status_code)
    print((r.text or '')[:400])
except Exception as e:
    print('PROBE_CONFIGURED_URL_ERROR', repr(e))

u2 = 'http://127.0.0.1:8002/creator-core/generate-blueprint'
try:
    r2 = requests.post(u2, json=p, timeout=5)
    print('PROBE_8002', u2, 'STATUS', r2.status_code)
    print((r2.text or '')[:400])
except Exception as e:
    print('PROBE_8002_ERROR', repr(e))
