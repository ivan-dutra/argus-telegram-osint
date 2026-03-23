import requests

print('Testando Ollama...')

try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        print('✅ Ollama funcionando!')
        models = r.json().get('models', [])
        print(f'Modelos: {len(models)}')
        for m in models:
            print(f'  - {m["name"]}')
    else:
        print('❌ Erro:', r.status_code)
except Exception as e:
    print('❌ Erro:', e)
    print('Execute: ollama serve')