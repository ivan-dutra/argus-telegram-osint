# 🚀 QUICK START GUIDE

## Configuração Inicial (apenas primeira vez)

### 1. Obter credenciais Telegram
- Acesse: https://my.telegram.org/apps
- Crie um app
- Copie `api_id` e `api_hash`

### 2. Editar config/config.yaml
```yaml
telegram:
  api_id: 12345678
  api_hash: "sua_hash_aqui"
  phone: "+5511999999999"
```

### 3. Instalar dependências
```bash
./setup.sh
```

---

## Comandos Principais

### Monitoramento Contínuo
```bash
python3 main.py
```
- Coleta mensagens em tempo real
- Gera relatórios automáticos a cada hora
- Pressione Ctrl+C para parar

### Gerar Relatório Agora
```bash
python3 main.py report
```

### Buscar Palavra-Chave
```bash
# Buscar hoje
python3 main.py search "trampo"

# Buscar últimos 7 dias
python3 main.py search "live 512267" 7
```

---

## Arquivos Importantes

- **config/config.yaml** - Suas configurações e keywords
- **data/osint.db** - Banco de dados com mensagens
- **data/reports/** - Relatórios gerados
- **logs/osint.log** - Logs do sistema

---

## Ajustar Sensibilidade

Abra `config/config.yaml` e altere:

```yaml
osint:
  relevance_threshold: 0.6  # Valores possíveis:
```

- **0.3-0.4**: Captura muitas mensagens (menos rigoroso)
- **0.5-0.6**: Balanceado ⭐ RECOMENDADO
- **0.7-0.8**: Apenas muito relevantes
- **0.9+**: Extremamente seletivo

---

## Keywords

Edite em `config/config.yaml`:

```yaml
osint:
  keywords:
    - trampo
    - gg
    - "live 512267"
    - "422061"
    - sua_keyword_aqui
```

**Dicas**:
- Use aspas para frases com espaços
- Seja específico para melhores resultados
- Comece com 3-5 keywords

---

## Problemas Comuns

### Ollama não está rodando
```bash
# Terminal 1
ollama serve

# Terminal 2
python3 main.py
```

### Código de verificação
Na primeira vez, o Telegram enviará um código. Digite quando solicitado.

### Muitas mensagens irrelevantes
Aumente o `relevance_threshold` para 0.7 ou 0.8

### Poucas mensagens
Diminua o `relevance_threshold` para 0.4 ou 0.5

---

## Estrutura dos Relatórios

Os relatórios mostram:

1. **Estatísticas Gerais** - Totais e taxas
2. **Análise por Grupo** - Resumo de cada grupo
3. **Análise Cruzada** - Conexões entre grupos
4. **Por Palavra-Chave** - Menções específicas

---

## Dicas de Uso

### 1. Primeira Execução
```bash
python3 main.py
# Aguarde coletar mensagens de hoje
# Ctrl+C depois de alguns minutos
python3 main.py report  # Ver o que capturou
```

### 2. Monitoramento 24/7
```bash
# Em um screen/tmux
screen -S osint
python3 main.py
# Ctrl+A, D para detach
```

### 3. Análise Pontual
```bash
# Não quer monitorar 24/7?
python3 main.py  # Deixa 1h rodando
# Ctrl+C
python3 main.py report  # Analisa o que coletou
```

---

## Backup

### Banco de Dados
```bash
cp data/osint.db data/backup_$(date +%Y%m%d).db
```

### Relatórios
```bash
tar -czf reports_backup.tar.gz data/reports/
```

---

## Performance

Seu sistema (32GB RAM + RTX 4050) é ideal!

- ✅ Qwen2.5 7B vai rodar perfeitamente
- ✅ Pode monitorar 50+ grupos simultaneamente
- ✅ Análise em tempo real sem lag

Se quiser MAIS VELOCIDADE:
```bash
ollama pull qwen2.5:4b-instruct
```

Depois em config.yaml:
```yaml
ollama:
  model: qwen2.5:4b-instruct
```

---

## Suporte

Verifique:
1. `logs/osint.log` - Logs detalhados
2. README.md - Documentação completa
3. Ollama está rodando: `curl http://localhost:11434/api/tags`

---

**Criado especialmente para levantamento OSINT em grupos do Telegram** 🔍
