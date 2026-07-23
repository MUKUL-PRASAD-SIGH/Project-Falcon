import json
data = json.load(open('data/karnataka_districts.geojson'))
features = data.get('features', [])
print(f'Districts loaded: {len(features)}')
print('Sample districts:', [f['properties'].get('dtname', '?') for f in features[:5]])
