# 🚀 SISTEMA DE PERFIS DINÂMICOS

## 🎯 **Visão Geral**

Agora você pode **trocar de contexto rapidamente** sem editar arquivos manualmente!

### **Recursos:**
- ✅ **Perfis pré-configurados** para diferentes contextos
- ✅ **Gerenciamento via linha de comando**
- ✅ **Troca instantânea** entre perfis
- ✅ **Importar/exportar** perfis
- ✅ **Adicionar keywords dinamicamente**

---

## 📋 **Perfis Pré-Configurados**

| Perfil | Descrição | Keywords |
|--------|-----------|----------|
| **carding** | Fraudes com cartões | 15 termos (gg, bin, live, cvv...) |
| **vazamentos** | Leaks e breaches | 13 termos (leak, dump, breach...) |
| **crypto** | Criptomoedas | 14 termos (bitcoin, eth, binance...) |
| **empregos** | Vagas de trabalho | 14 termos (trampo, vaga, freela...) |
| **tech** | Tecnologia geral | 14 termos (python, react, ai...) |
| **ecommerce** | Vendas online | 13 termos (shopify, dropshipping...) |
| **marketing** | Marketing digital | 13 termos (tráfego, ads, seo...) |
| **gaming** | Jogos e gamers | 13 termos (game, steam, twitch...) |
| **investimentos** | Mercado financeiro | 13 termos (ações, b3, fundos...) |
| **infosec** | Segurança da info | 14 termos (pentest, malware...) |

---

## 🎮 **Uso Rápido**

### **Ver perfis disponíveis:**
```powershell
python keyword_manager.py profiles
```

### **Ativar um perfil:**
```powershell
# Monitorar fraudes
python keyword_manager.py activate carding

# Monitorar criptomoedas
python keyword_manager.py activate crypto

# Monitorar vagas de emprego
python keyword_manager.py activate empregos
```

### **Ver keywords ativas:**
```powershell
python keyword_manager.py list
```

---

## ✏️ **Gerenciamento de Keywords**

### **Adicionar keywords:**
```powershell
# Adicionar ao perfil ativo
python keyword_manager.py add "nova" "keyword" "aqui"

# Adicionar a perfil específico
python keyword_manager.py add-to carding "brute" "spoof"
```

### **Remover keywords:**
```powershell
python keyword_manager.py remove "keyword1" "keyword2"
```

### **Limpar todas:**
```powershell
python keyword_manager.py clear
```

---

## 🎨 **Criar Perfis Personalizados**

### **Exemplo 1: Monitorar Bitcoin**
```powershell
python keyword_manager.py create bitcoin "Monitorar apenas Bitcoin" "bitcoin" "btc" "satoshi" "lightning network"
```

### **Exemplo 2: Monitorar NFTs**
```powershell
python keyword_manager.py create nfts "NFTs e arte digital" "nft" "opensea" "mint" "gas" "eth" "floor price"
```

### **Exemplo 3: Monitorar Política**
```powershell
python keyword_manager.py create politica "Discussões políticas" "eleição" "voto" "candidato" "partido"
```

### **Exemplo 4: Monitorar Saúde**
```powershell
python keyword_manager.py create saude "Saúde e bem-estar" "médico" "consulta" "remédio" "sintomas" "tratamento"
```

---

## 📊 **Ajustar Sensibilidade**

### **Ver threshold atual:**
```powershell
python keyword_manager.py threshold
```

### **Definir threshold:**
```powershell
# Capturar MAIS mensagens (permissivo)
python keyword_manager.py threshold 0.4

# Balanceado
python keyword_manager.py threshold 0.6

# Capturar MENOS mensagens (restritivo)
python keyword_manager.py threshold 0.8
```

---

## 💾 **Importar/Exportar Perfis**

### **Exportar perfil:**
```powershell
# Exportar para compartilhar ou backup
python keyword_manager.py export carding perfil_carding.json
```

### **Importar perfil:**
```powershell
# Importar perfil de outra pessoa
python keyword_manager.py import novo_perfil perfil_recebido.json
```

---

## 🔥 **Fluxo de Trabalho Sugerido**

### **Cenário 1: Investigação de Fraudes (Manhã)**
```powershell
# Ativar perfil de carding
python keyword_manager.py activate carding

# Iniciar monitoramento
python main.py

# Deixar rodando por 3-4 horas...
```

### **Cenário 2: Buscar Emprego (Tarde)**
```powershell
# Parar monitoramento (Ctrl+C)

# Trocar para perfil de empregos
python keyword_manager.py activate empregos

# Adicionar keywords específicas
python keyword_manager.py add "python" "sênior" "remoto"

# Reiniciar
python main.py
```

### **Cenário 3: Monitorar Crypto (Noite)**
```powershell
# Trocar perfil
python keyword_manager.py activate crypto

# Adicionar moedas específicas
python keyword_manager.py add "solana" "cardano" "polygon"

# Monitorar
python main.py
```

---

## 🎯 **Casos de Uso Avançados**

### **1. Investigação Multi-Tópico**

```powershell
# Criar perfil abrangente
python keyword_manager.py create investigacao "Investigação ampla" "fraude" "golpe" "suspeito" "crime" "polícia"

# Ativar
python keyword_manager.py activate investigacao
```

### **2. Monitoramento de Marca**

```powershell
# Monitorar menções à sua empresa
python keyword_manager.py create minha_marca "Monitorar reputação" "MinhaEmpresa" "MeuProduto" "reclamação" "suporte"
```

### **3. Pesquisa Acadêmica**

```powershell
# Monitorar tópicos de pesquisa
python keyword_manager.py create pesquisa "Pesquisa científica" "paper" "pesquisa" "estudo" "artigo" "dados"
```

### **4. Monitorar Concorrentes**

```powershell
python keyword_manager.py create concorrentes "Inteligência competitiva" "EmpresaX" "EmpresaY" "produto rival" "preço"
```

---

## 🔄 **Rotação Automática de Perfis**

### **Cenário: Monitorar 3 tópicos em 24h**

```powershell
# 8h Fraudes (00:00 - 08:00)
python keyword_manager.py activate carding
python main.py  # Deixar rodando 8h

# 8h Crypto (08:00 - 16:00)
python keyword_manager.py activate crypto
python main.py

# 8h Empregos (16:00 - 00:00)
python keyword_manager.py activate empregos
python main.py
```

---

## 📦 **Compartilhar Perfis**

### **Exportar seus perfis:**

```powershell
# Exportar todos os perfis úteis
python keyword_manager.py export carding carding_profile.json
python keyword_manager.py export crypto crypto_profile.json

# Compartilhar os arquivos .json
```

### **Receber perfis de outros:**

```powershell
# Baixar perfil compartilhado
# Importar no seu sistema
python keyword_manager.py import darkweb darkweb_profile.json
python keyword_manager.py activate darkweb
```

---

## ⚡ **Atalhos e Dicas**

### **1. Criar perfil rápido:**
```powershell
python keyword_manager.py create temp "Temporário" "keyword1" "keyword2"
python keyword_manager.py activate temp
```

### **2. Adicionar múltiplas keywords:**
```powershell
python keyword_manager.py add "kw1" "kw2" "kw3" "kw4" "kw5"
```

### **3. Ver keywords antes de ativar:**
```powershell
# Ver perfil
python keyword_manager.py profiles

# Ativar
python keyword_manager.py activate nome_perfil
```

---

## 🛠️ **Troubleshooting**

### **Perfil não aparece:**
```powershell
# Verificar arquivo
notepad config\profiles.yaml
```

### **Keywords não estão funcionando:**
```powershell
# Verificar keywords ativas
python keyword_manager.py list

# Verificar threshold
python keyword_manager.py threshold
```

### **Resetar tudo:**
```powershell
# Limpar keywords
python keyword_manager.py clear

# Ativar perfil padrão
python keyword_manager.py activate carding
```

---

## 📊 **Estatísticas por Perfil**

Após monitorar com um perfil, gere relatório:

```powershell
# Gerar relatório
python main.py report

# Ver resultados em data/reports/
```

---

## 🎓 **Exemplos Práticos Completos**

### **Exemplo 1: Investigador de Fraudes**

```powershell
# Manhã - Fraudes gerais
python keyword_manager.py activate carding
python main.py &  # Rodar em background

# Tarde - Vazamentos específicos
python keyword_manager.py activate vazamentos
python keyword_manager.py add "empresa X" "cpf"
python main.py

# Noite - Relatórios
python main.py report
python main.py search "422061"
```

### **Exemplo 2: Trader de Crypto**

```powershell
# Criar perfil específico
python keyword_manager.py create mycoins "Minhas moedas" "btc" "eth" "sol" "ada"

# Adicionar termos de análise
python keyword_manager.py add-to mycoins "alta" "baixa" "resistência" "suporte"

# Monitorar
python keyword_manager.py activate mycoins
python main.py
```

### **Exemplo 3: Recrutador Tech**

```powershell
# Perfil de vagas tech
python keyword_manager.py create vagas_tech "Vagas de tecnologia" "python" "javascript" "react" "sênior" "pleno" "júnior" "vaga" "remoto"

# Ativar e monitorar
python keyword_manager.py activate vagas_tech
python main.py

# Gerar relatório de vagas
python main.py report
```

---

## 🔐 **Segurança**

- ✅ Perfis ficam em `config/profiles.yaml`
- ✅ Não committar perfis sensíveis no git
- ✅ Usar perfis diferentes para contextos diferentes
- ✅ Exportar backup regularmente

---

**🚀 Agora você tem controle total sobre o monitoramento!**

Troque de contexto em segundos e monitore qualquer assunto em qualquer grupo!
