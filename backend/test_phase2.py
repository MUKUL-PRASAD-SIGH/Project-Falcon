"""Phase 2 endpoint smoke test — run from project root."""
import urllib.request, json, time

BASE = 'http://localhost:8000'
tests = [
    ('GET /', '/'),
    ('GET /health', '/health'),
    ('GET /api/districts (cold)', '/api/districts'),
    ('GET /api/clusters (cold)', '/api/clusters'),
    ('GET /api/districts (warm)', '/api/districts'),
    ('GET /api/clusters (warm)', '/api/clusters'),
    ('GET /api/stats', '/api/stats'),
    ('GET /api/forecast', '/api/forecast'),
    ('GET /api/offender/risk/1', '/api/offender/risk/1'),
    ('GET /api/anomalies', '/api/anomalies'),
    ('GET /api/cases/similar?case_id=1', '/api/cases/similar?case_id=1'),
    ('GET /api/graph/accused/1', '/api/graph/accused/1'),
    ('GET /api/graph/gangs', '/api/graph/gangs'),
    ('GET /api/forensics/criteria', '/api/forensics/criteria'),
    ('GET /api/admin/stats', '/api/admin/stats'),
]

results = []
for label, path in tests:
    try:
        t0 = time.perf_counter()
        with urllib.request.urlopen(BASE + path, timeout=15) as resp:
            body = json.loads(resp.read())
            ms = round((time.perf_counter() - t0) * 1000)
            extra = ''
            if 'districts' in path and 'admin' not in path:
                src = body.get('source', '?')
                cnt = len(body.get('districts', []))
                extra = f'src={src} cnt={cnt}'
            elif 'clusters' in path:
                src = body.get('source', '?')
                cnt = body.get('feature_count', '?')
                extra = f'src={src} features={cnt}'
            elif 'forecast' in path:
                keys = body.get('all_districts', [])
                has_chart = 'chart_data' in body
                extra = f'{len(keys)} districts chart_data={has_chart}'
            elif 'risk' in path:
                score = body.get('data', {}).get('risk_score', '?')
                extra = f'risk_score={score}'
            elif 'anomalies' in path:
                cnt = body.get('count', '?')
                extra = f'count={cnt}'
            elif 'forensics/criteria' in path:
                criteria = list(body.get('rubric', {}).keys())
                extra = ' | '.join(criteria)
            elif 'admin/stats' in path:
                d = body.get('data', {})
                extra = f"firs={d.get('total_firs','?')} offenders={d.get('total_offenders','?')}"
            results.append((label, ms, 'PASS', extra))
    except Exception as e:
        results.append((label, 0, 'FAIL', str(e)[:80]))

print()
print('=' * 84)
print('  Phase 2 — Endpoint Smoke Test Results')
print('=' * 84)
for label, ms, result, notes in results:
    icon = 'OK  ' if result == 'PASS' else 'FAIL'
    bar = f'{ms:>6}ms'
    print(f'  [{icon}] {label:<44} {bar}  {notes}')
print('=' * 84)
passes = sum(1 for _, _, r, _ in results if r == 'PASS')
print(f'\n  {passes}/{len(results)} endpoints passing\n')

# Cache warm/cold comparison
cold_d = next((r for r in results if 'districts (cold)' in r[0]), None)
warm_d = next((r for r in results if 'districts (warm)' in r[0]), None)
if cold_d and warm_d:
    print(f'  Cache effect on /api/districts:')
    print(f'    Cold miss: {cold_d[1]}ms')
    print(f'    Warm hit:  {warm_d[1]}ms')
    speedup = round(cold_d[1] / max(warm_d[1], 1), 1)
    print(f'    Speedup:   {speedup}x\n')
