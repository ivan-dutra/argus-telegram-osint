⚠️ Este projeto é voltado para análise de segurança, OSINT e detecção de padrões suspeitos.
Não deve ser utilizado para atividades ilegais. Não me responsabilizo pelo mal uso, ou quaisquer, atividades que infrinjam as leis do seu país. Uso somente educacional e em ambiente controlado.




# 🔍 Argus Telegram OSINT Bot

Sistema de monitoramento e análise em tempo real de grupos do Telegram, usando IA local (Ollama) para análise inteligente de mensagens.

## 🎯 Funcionalidades

- ✅ Monitoramento em tempo real de todos os grupos do Telegram
- ✅ Análise de relevância com IA (Ollama + Qwen2.5)
- ✅ Filtro inteligente por palavras-chave
- ✅ Busca semântica com embeddings
- ✅ Geração automática de relatórios OSINT
- ✅ Análise cruzada entre múltiplos grupos
- ✅ Tracking de usuários e atividades
- ✅ Base de dados SQLite com histórico
- ✅ Relatórios em Markdown

## 📋 Pré-requisitos

### 1. Ollama Instalado
Você já tem! Verifique com:
```bash
ollama list
```

### 2. Python 3.8+
```bash
python3 --version
```

### 3. Credenciais do Telegram
Acesse [https://my.telegram.org/apps](https://my.telegram.org/apps) e crie um app para obter:
- `api_id`
- `api_hash`

## 🚀 Instalação

### 1. Instalar dependências
```bash
cd telegram-osint-bot
pip install -r requirements.txt --break-system-packages
```

### 2. Configurar credenciais
Edite o arquivo `config/config.yaml`:

```yaml
telegram:
  api_id: 12345678  # Seu API ID
  api_hash: "abcdef1234567890"  # Seu API Hash
  phone: "+5511999999999"  # Seu telefone com código do país

ollama:
  model: qwen2.5:7b-instruct  # Modelo para análise
  embedding_model: nomic-embed-text:latest  # Para embeddings

osint:
  keywords:
    - visa
    - mastercard
    - cc
    relevance_threshold: 0.6  # 0-1, quanto maior mais restritivo
```

### 3. Primeira execução
```bash
python3 main.py
```

Na primeira vez, você precisará:
1. Inserir o código de verificação que receberá no Telegram
2. Se tiver 2FA, inserir a senha

## 📖 Uso

### Monitoramento em Tempo Real
```bash
python3 main.py
```

Isso irá:
- Conectar ao Telegram
- Carregar todos os seus grupos
- Coletar mensagens de hoje
- Começar a monitorar novas mensagens em tempo real
- Gerar relatórios automáticos a cada hora

### Gerar Relatório Imediato
```bash
python3 main.py report
```

### Buscar por Palavra-Chave
```bash
# Buscar hoje
python3 main.py search "trampo"

# Buscar últimos 7 dias
python3 main.py search "gg" 7
```

## 📊 Relatórios

Os relatórios são salvos em `data/reports/` em formato Markdown.

Exemplo de relatório:

```markdown
# 🔍 RELATÓRIO OSINT - 2026-01-12

## 📈 ESTATÍSTICAS GERAIS
- Total de Mensagens Processadas: 1,234
- Mensagens Relevantes: 89
- Grupos Monitorados: 15
- Taxa de Relevância: 7.2%

## 📱 ANÁLISE POR GRUPO

### 🔸 Grupo BINs Brasil
Mensagens relevantes: 23

📊 RESUMO DO GRUPO
- Principais tópicos: Discussão sobre BINs válidos para teste
- Usuários mais ativos: @user1, @user2, @user3
- Informações relevantes: Live 512267 confirmada ativa
- Padrões identificados: Aumento de atividade às 14h

🔥 Destaques:
- [@user1] (14:23): Live 512267 está passando no site X
  Score: 0.92
- [@user2] (15:45): Novo método para validação de cartões
  Score: 0.87

## 🔗 ANÁLISE CRUZADA
Identificadas conexões entre Grupo A e Grupo B...
```

## 🔧 Configurações Avançadas

### Ajustar Sensibilidade
No `config/config.yaml`:

```yaml
osint:
  relevance_threshold: 0.6  # Valores:
    # 0.0-0.4: Muito permissivo (muitas mensagens)
    # 0.5-0.6: Balanceado (recomendado)
    # 0.7-0.9: Restritivo (apenas muito relevantes)
    # 0.9-1.0: Extremamente restritivo
```

### Trocar Modelo Ollama
```yaml
ollama:
  model: deepseek-r1:8b  # Modelo alternativo
```

### Adicionar/Remover Keywords
```yaml
osint:
  keywords:
    - palavra1
    - palavra2
    - "frase com espaços"
```

## 📁 Estrutura do Projeto

```
telegram-osint-bot/
├── main.py                 # Script principal
├── config/
│   └── config.yaml        # Configurações
├── src/
│   ├── database.py        # Gerenciamento SQLite
│   ├── ollama_client.py   # Integração com Ollama
│   ├── telegram_monitor.py # Monitor do Telegram
│   └── report_generator.py # Gerador de relatórios
├── data/
│   ├── osint.db          # Base de dados
│   └── reports/          # Relatórios gerados
└── logs/
    └── osint.log         # Logs do sistema
```

## 🛡️ Segurança

⚠️ **IMPORTANTE**:
- Mantenha suas credenciais seguras
- Não compartilhe o arquivo `config/config.yaml`
- O arquivo de sessão (`.session`) contém suas credenciais
- Use em ambiente controlado

## 🐛 Troubleshooting

### Erro: "Ollama não está disponível"
```bash
# Inicie o Ollama
ollama serve

# Em outro terminal
python3 main.py
```

### Erro: "API hash/ID inválido"
Verifique se copiou corretamente de [https://my.telegram.org/apps](https://my.telegram.org/apps)

### Muitas mensagens irrelevantes
Aumente o `relevance_threshold` no config:
```yaml
relevance_threshold: 0.7  # De 0.6 para 0.7
```

### Poucas mensagens
Diminua o threshold ou adicione mais keywords:
```yaml
relevance_threshold: 0.5
keywords:
  - palavra1
  - palavra2
  - palavra3
```

## 📈 Performance

### Hardware Recomendado
- **RAM**: 16GB+ (seu sistema tem 32GB ✅)
- **GPU**: RTX 4050 ou melhor (você tem! ✅)
- **CPU**: 4+ cores
- **Disco**: 10GB+ livre

### Otimizações
O Qwen2.5 7B é otimizado para sua RTX 4050. Se quiser mais velocidade:

```bash
# Usar modelo menor
ollama pull qwen2.5:4b-instruct

# Atualizar config.yaml
model: qwen2.5:4b-instruct
```

## 🔄 Manutenção

### Limpeza de Dados Antigos
Configurado automaticamente:
```yaml
osint:
  history_days: 7  # Mantém últimos 7 dias
```

### Backup
```bash
# Backup do banco de dados
cp data/osint.db data/osint_backup_$(date +%Y%m%d).db

# Backup de relatórios
tar -czf reports_backup.tar.gz data/reports/
```

## 📝 Exemplos de Uso

### Caso de Uso 1: Monitorar BINs
```yaml
keywords:
  - bank identification number
  - credit card number
  - name of bank

```

### Caso de Uso 2: Monitorar Ofertas de Trabalho
```yaml
keywords:
  - trampo
  - vaga
  - freela
  - trabalho remoto
  - desenvolvedor
```

### Caso de Uso 3: Análise de Ameaças
```yaml
keywords:
  - leak
  - database
  - dump
  - breach
  - exploit
```

## 🤝 Contribuindo

Este é um projeto pessoal, mas sugestões são bem-vindas!

## ⚖️ Disclaimer

Este software é para fins educacionais e de pesquisa OSINT legítima. 
Use de forma ética e respeitando a privacidade dos usuários.

## 📄 Licença

MIT License - Use por sua conta e risco

---

**Desenvolvido por Ivan Dutra utilizando Ollama + Python + Telegram**



