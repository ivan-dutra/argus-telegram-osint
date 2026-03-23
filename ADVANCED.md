# 🎯 GUIA DE USO AVANÇADO

## Cenários de Uso Práticos

### 1. Monitoramento de BINs e Lives

**Objetivo**: Identificar quando BINs específicos são mencionados e em que contexto.

#### Configuração
```yaml
osint:
  keywords:
    - "512267"
    - "422061"
    - "424631"
    - live
    - bin
    - aprovando
    - passando
  relevance_threshold: 0.6
```

#### Análise
```bash
# Monitorar em tempo real
python3 main.py

# Buscar menções específicas
python3 main.py search "512267" 7

# Gerar relatório
python3 main.py report
```

**O que o bot identifica:**
- Usuários que postam BINs
- Sites onde estão "passando"
- Horários de maior atividade
- Conexões entre diferentes grupos
- Padrões de comportamento

---

### 2. Intelligence de Trabalho/Freelas

**Objetivo**: Mapear oportunidades de trabalho remoto e freelas.

#### Configuração
```yaml
osint:
  keywords:
    - trampo
    - freela
    - vaga
    - trabalho remoto
    - desenvolvedor
    - programador
    - python
    - javascript
    - $$$  # Menções a valores
  relevance_threshold: 0.5
```

#### Análise Avançada
```python
# Criar script customizado: analyze_jobs.py

from src.database import OSINTDatabase
from src.ollama_client import OllamaClient

db = OSINTDatabase('data/osint.db')
ollama = OllamaClient(
    base_url="http://localhost:11434",
    model="qwen2.5:7b-instruct",
    embedding_model="nomic-embed-text:latest"
)

# Buscar vagas
messages = db.get_messages_by_keyword('trampo', days=7)

# Extrair informações estruturadas
for msg in messages:
    prompt = f"""
    Extraia informações estruturadas desta mensagem:
    
    {msg['text']}
    
    Retorne JSON com:
    - tipo_trabalho (freela/clt/pj)
    - tecnologias (array)
    - valor_mencionado (se houver)
    - remoto (sim/não)
    - contato (se houver)
    """
    
    resultado = ollama.generate(prompt)
    print(resultado)
```

---

### 3. Tracking de Usuários Específicos

**Objetivo**: Monitorar atividades de usuários de interesse.

#### Script Customizado
```python
# user_tracker.py

import asyncio
from src.telegram_monitor import TelegramMonitor
from src.database import OSINTDatabase
from src.ollama_client import OllamaClient

# Usuários de interesse
USUARIOS_ALVO = ['user1', 'user2', 'user3']

async def track_users():
    # Inicializar componentes
    db = OSINTDatabase('data/osint.db')
    
    # Buscar atividades
    messages = db.get_today_messages()
    
    for username in USUARIOS_ALVO:
        user_msgs = [m for m in messages if m['username'] == username]
        
        if user_msgs:
            print(f"\n👤 @{username} - {len(user_msgs)} mensagens")
            
            for msg in user_msgs:
                print(f"  [{msg['date']}] {msg['group_name']}")
                print(f"  {msg['text'][:100]}...")
                print()

asyncio.run(track_users())
```

---

### 4. Detecção de Padrões e Alertas

**Objetivo**: Identificar padrões suspeitos e gerar alertas.

#### Configuração com Alertas
```python
# alert_system.py

from src.database import OSINTDatabase
from src.ollama_client import OllamaClient
import smtplib
from email.mime.text import MIMEText

class AlertSystem:
    def __init__(self):
        self.db = OSINTDatabase('data/osint.db')
        self.ollama = OllamaClient(...)
    
    def check_patterns(self):
        messages = self.db.get_today_messages(min_relevance=0.8)
        
        # Padrão 1: Múltiplas menções ao mesmo BIN
        bin_mentions = {}
        for msg in messages:
            for keyword in ['512267', '422061']:
                if keyword in msg['text']:
                    bin_mentions[keyword] = bin_mentions.get(keyword, 0) + 1
        
        for bin_num, count in bin_mentions.items():
            if count >= 5:  # 5+ menções = alerta
                self.send_alert(
                    f"⚠️ BIN {bin_num} mencionado {count}x hoje!"
                )
        
        # Padrão 2: Usuário muito ativo
        user_activity = {}
        for msg in messages:
            username = msg['username']
            user_activity[username] = user_activity.get(username, 0) + 1
        
        for user, count in user_activity.items():
            if count >= 20:  # 20+ msgs = suspeito
                self.send_alert(
                    f"⚠️ @{user} muito ativo: {count} mensagens!"
                )
    
    def send_alert(self, message):
        # Implementar notificação
        # Pode ser email, Telegram, Discord, etc
        print(f"🚨 ALERTA: {message}")

# Rodar periodicamente
if __name__ == '__main__':
    alert = AlertSystem()
    alert.check_patterns()
```

---

### 5. Análise de Sentimento e Tendências

**Objetivo**: Identificar o "clima" dos grupos e tendências.

```python
# sentiment_analysis.py

from src.database import OSINTDatabase
from src.ollama_client import OllamaClient
from collections import Counter
import json

db = OSINTDatabase('data/osint.db')
ollama = OllamaClient(...)

# Mensagens de hoje
messages = db.get_today_messages()

# Análise de sentimento
sentiments = []
topics = []

for msg in messages:
    analysis = msg['analysis']
    
    # Sentimento (pode adicionar ao ollama_client.py)
    prompt = f"""
    Analise o sentimento desta mensagem:
    "{msg['text']}"
    
    Retorne apenas: positivo, negativo ou neutro
    """
    
    sentiment = ollama.generate(prompt).strip().lower()
    sentiments.append(sentiment)
    
    # Tópico
    topic = analysis.get('topico_principal', 'geral')
    topics.append(topic)

# Estatísticas
print("📊 ANÁLISE DE SENTIMENTO")
print(Counter(sentiments))

print("\n📈 TÓPICOS MAIS DISCUTIDOS")
print(Counter(topics).most_common(10))
```

---

### 6. Exportação para Outras Ferramentas

#### Exportar para Maltego
```python
# export_maltego.py

from src.database import OSINTDatabase
import csv

db = OSINTDatabase('data/osint.db')
messages = db.get_today_messages()

# CSV para Maltego
with open('maltego_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Username', 'Group', 'Message', 'Date', 'Score'])
    
    for msg in messages:
        writer.writerow([
            msg['username'],
            msg['group_name'],
            msg['text'][:200],
            msg['date'],
            msg['relevance_score']
        ])

print("✅ Exportado para maltego_export.csv")
```

#### Exportar para Gephi (análise de grafos)
```python
# export_gephi.py

from src.database import OSINTDatabase
import json

db = OSINTDatabase('data/osint.db')
messages = db.get_today_messages()

# Criar grafo de conexões
nodes = set()
edges = []

for msg in messages:
    # Nó do usuário
    nodes.add(msg['username'])
    
    # Nó do grupo
    nodes.add(msg['group_name'])
    
    # Aresta usuário -> grupo
    edges.append({
        'source': msg['username'],
        'target': msg['group_name'],
        'weight': msg['relevance_score']
    })

# Formato Gephi
graph = {
    'nodes': [{'id': node} for node in nodes],
    'edges': edges
}

with open('gephi_export.json', 'w') as f:
    json.dump(graph, f, indent=2)

print("✅ Exportado para gephi_export.json")
```

---

### 7. Integração com Outras APIs

#### Enriquecer com dados externos
```python
# enrich_data.py

import requests
from src.database import OSINTDatabase

db = OSINTDatabase('data/osint.db')

# Exemplo: Verificar BINs em API externa
def check_bin(bin_number):
    # API fictícia
    response = requests.get(f'https://api.binlist.net/{bin_number}')
    if response.status_code == 200:
        data = response.json()
        return {
            'banco': data.get('bank', {}).get('name'),
            'tipo': data.get('type'),
            'marca': data.get('brand')
        }
    return None

# Processar mensagens
messages = db.get_messages_by_keyword('bin', days=1)

for msg in messages:
    # Extrair BINs (regex)
    import re
    bins = re.findall(r'\b\d{6}\b', msg['text'])
    
    for bin_num in bins:
        info = check_bin(bin_num)
        if info:
            print(f"BIN {bin_num}: {info['banco']} - {info['tipo']}")
```

---

### 8. Machine Learning Personalizado

#### Treinar classificador customizado
```python
# train_classifier.py

from src.database import OSINTDatabase
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

db = OSINTDatabase('data/osint.db')

# Coletar mensagens rotuladas
messages = db.get_today_messages()

# Preparar dados
texts = [msg['text'] for msg in messages]
labels = [1 if msg['relevance_score'] > 0.7 else 0 for msg in messages]

# Vetorizar
vectorizer = TfidfVectorizer(max_features=500)
X = vectorizer.fit_transform(texts)

# Treinar
clf = MultinomialNB()
clf.fit(X, labels)

# Usar para prever novas mensagens
def predict_relevance(text):
    X_new = vectorizer.transform([text])
    return clf.predict_proba(X_new)[0][1]

# Teste
test_msg = "Galera, live 512267 passando!"
score = predict_relevance(test_msg)
print(f"Score ML: {score:.2f}")
```

---

## Dicas de Performance

### 1. Processamento em Lote
Ao invés de analisar uma mensagem por vez, agrupe:

```python
# Mais eficiente
messages_batch = []
for msg in new_messages:
    messages_batch.append(msg)
    
    if len(messages_batch) >= 10:
        # Processar lote de 10
        analyze_batch(messages_batch)
        messages_batch = []
```

### 2. Cache de Embeddings
Evite recalcular embeddings:

```python
# Adicionar à database.py
def get_or_create_embedding(self, text):
    # Verificar cache
    cached = self.get_cached_embedding(text)
    if cached:
        return cached
    
    # Gerar novo
    embedding = self.ollama.get_embedding(text)
    self.cache_embedding(text, embedding)
    return embedding
```

### 3. Filtros Rápidos Antes da IA
Use regex e buscas simples antes de chamar IA:

```python
# Filtro rápido
def quick_filter(text, keywords):
    text_lower = text.lower()
    
    # Palavras de stop
    if len(text) < 10:
        return False
    
    # Deve ter ao menos 1 keyword
    has_keyword = any(kw.lower() in text_lower for kw in keywords)
    if not has_keyword:
        return False
    
    # Passou filtro rápido, pode usar IA
    return True
```

---

## Troubleshooting Avançado

### Ollama muito lento
```bash
# Usar modelo menor
ollama pull qwen2.5:4b-instruct

# Ou usar quantização mais agressiva
ollama pull qwen2.5:3b-instruct
```

### Muita RAM sendo usada
```python
# Limitar contexto do Ollama
ollama = OllamaClient(
    model="qwen2.5:7b-instruct",
    max_tokens=1024  # Reduzir de 2048
)
```

### Banco de dados grande
```bash
# Compactar
sqlite3 data/osint.db "VACUUM;"

# Limpar antigos
python3 -c "
from src.database import OSINTDatabase
db = OSINTDatabase('data/osint.db')
db.cleanup_old_data(days=3)  # Manter apenas 3 dias
"
```

---

## Próximos Passos

1. **Implementar Webhook**: Receber alertas em tempo real
2. **Dashboard Web**: Visualizar dados com Flask/FastAPI
3. **Análise de Imagens**: Usar modelos vision para screenshots
4. **Multi-idioma**: Treinar em português BR
5. **Telegram Bot Interface**: Consultar via bot do Telegram

---

**Para mais informações, consulte README.md e QUICKSTART.md**
