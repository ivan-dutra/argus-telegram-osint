#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         🔍 TELEGRAM OSINT BOT by @ivm4nsec              ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Verificar Ollama
echo ""
echo "🤖 Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama não encontrado!"
    echo "Instale em: https://ollama.ai"
    exit 1
fi
echo "✅ Ollama instalado"

# Verificar se Ollama está rodando
echo ""
echo "🔍 Verificando se Ollama está rodando..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama não está rodando!"
    echo "Execute em outro terminal: ollama serve"
    echo ""
    read -p "Pressione Enter quando Ollama estiver rodando..."
fi
echo "✅ Ollama está rodando"

# Verificar modelos
echo ""
echo "📦 Verificando modelos necessários..."

if ! ollama list | grep -q "qwen2.5:7b-instruct"; then
    echo "⚠️  Modelo qwen2.5:7b-instruct não encontrado"
    read -p "Baixar agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        ollama pull qwen2.5:7b-instruct
    fi
fi

if ! ollama list | grep -q "nomic-embed-text"; then
    echo "⚠️  Modelo nomic-embed-text não encontrado"
    read -p "Baixar agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        ollama pull nomic-embed-text:latest
    fi
fi

echo "✅ Modelos prontos"

# Instalar dependências Python
echo ""
echo "📚 Instalando dependências Python..."
pip install -r requirements.txt --break-system-packages --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Criar diretórios
echo ""
echo "📁 Criando diretórios..."
mkdir -p data/reports logs
echo "✅ Diretórios criados"

# Verificar config
echo ""
echo "⚙️  Verificando configuração..."
if [ ! -f "config/config.yaml" ]; then
    echo "❌ Arquivo config/config.yaml não encontrado!"
    exit 1
fi

# Verificar credenciais
if grep -q "YOUR_API_ID" config/config.yaml; then
    echo "⚠️  ATENÇÃO: Configure suas credenciais do Telegram!"
    echo ""
    echo "1. Acesse: https://my.telegram.org/apps"
    echo "2. Crie um app e obtenha api_id e api_hash"
    echo "3. Edite config/config.yaml com suas credenciais"
    echo ""
    exit 1
fi

echo "✅ Configuração ok"

# Sucesso
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         ✅ SETUP COMPLETO!                              ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Para iniciar o bot:"
echo "   python3 main.py"
echo ""
echo "📖 Para mais informações:"
echo "   cat README.md"
echo ""
