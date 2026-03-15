import json

with open('verified_templates.json', encoding='utf-8') as f:
    d = json.load(f)

print('Keys:', list(d.keys()))
print('Candidate keys:', list(d['candidates'][0].keys()))
print()
for c in d['candidates']:
    has_job = 'job_desc' in c
    print(f"{c['name']} ({c['role']}): conf={c['confidence']}% | resume={len(c['resume'])}chars | has_job_desc={has_job}")
