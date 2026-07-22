import urllib.request, json, time

BASE = 'http://localhost:8000'
tests = [
    ('GET /', '/'),
    ('GET /health', '/health'),
    ('GET /api/districts', '/api/districts'),
    ('GET /api/clusters', '/api/clusters'),
    ('GET /api/stats', '/api/stats'),
    ('GET /api/forecast', '/api/forecast'),
    ('GET /api/offender/risk/1', '/api/offender/risk/1'),
    ('GET /api/anomalies', '/api/anomalies'),
    ('GET /api/cases/similar?case_id=1', '/api/cases/similar?case_id=1'),
    ('GET /api/graph/accused/1', '/api/graph/accused/1'),
    ('GET /api/forensics/criteria', '/api/forensics/criteria'),
    ('GET /api/admin/stats', '/api/admin/stats'),
]

results = []
for label, path in tests:
    try:
        t0 = time.perf_counter()
        with urllib.request.urlopen(BASE + path, timeout=10) as resp:
            body = json.loads(resp.read())
            ms = round((time.perf_counter() - t0) * 1000)
            status = body.get('status', 'ok')
            # extra details per endpoint
            extra = ''
            if path == '/api/districts':
                src = body.get('source', '?')
                cnt = len(body.get('districts', []))
                extra = f"source={src}, {cnt} districts"
            elif path == '/api/clusters':
                src = body.get('source', '?')
                cnt = body.get('feature_count', '?')
                extra = f"source={src}, {cnt} features"
            elif path == '/api/forecast':
                keys = list(body.get('all_districts', []))
                extra = f"{len(keys)} districts, chart_data={'chart_data' in body}"
            elif path == '/api/offender/risk/1':
                score = body.get('data', {}).get('risk_score', '?')
                extra = f"risk_score={score}"
            elif path == '/api/anomalies':
                cnt = body.get('count', '?')
                extra = f"{cnt} anomalies"
            elif path == '/api/forensics/criteria':
                criteria = list(body.get('rubric', {}).keys())
                extra = ', '.join(criteria)
            results.append((label, ms, 'PASS', extra or status))
    except Exception as e:
        results.append((label, 0, 'FAIL', str(e)[:70]))

print()
print('Phase 2 Endpoint Smoke Test Results')
print('=' * 80)
print(f"  {'Endpoint':<42} {'ms':>6}  {'Result'}  Notes")
print('=' * 80)
for label, ms, result, notes in results:
    icon = 'v' if result == 'PASS' else 'X'
    print(f"  [{icon}] {label:<40} {ms:>6}ms  {result:<6}  {notes}")
print('=' * 80)
passes = sum(1 for _, _, r, _ in results if r == 'PASS')
print(f"\n  {passes}/{len(results)} endpoints passing\n")
