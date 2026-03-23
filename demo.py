#!/usr/bin/env python3
"""
Demo Script - Testa os componentes sem conectar ao Telegram
Útil para verificar se Ollama e análise estão funcionando
"""

import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ollama_client import OllamaClient
import json

print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🧪 DEMO - TESTE DE ANÁLISE                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

# Mensagens de exemplo
MENSAGENS_TESTE = [
    {
        "texto": "Galera, descobri uma live 512267 que tá passando no site X! Testei aqui e funcionou",
        "username": "user1",
        "date": "2026-01-12 14:30"
    },
    {
        "texto": "Alguém sabe se o 422061 ainda tá ativo? Preciso urgente",
        "username": "user2",
        "date": "2026-01-12 15:45"
    },
    {
        "texto": "Pessoal, to procurando trampo como dev Python, alguém conhece algo?",
        "username": "user3",
        "date": "2026-01-12 16:20"
    },
    {
        "texto": "Bom dia pessoal! Como estão?",
        "username": "user4",
        "date": "2026-01-12 09:00"
    },
    {
        "texto": "Encontrei um gg muito bom, quem quiser chama no PV",
        "username": "user5",
        "date": "2026-01-12 17:10"
    }
]

KEYWORDS = ["trampo", "gg", "live 512267", "422061"]

print("🤖 Inicializando Ollama...")
try:
    ollama = OllamaClient(
        base_url="http://localhost:11434",
        model="qwen2.5:7b-instruct",
        embedding_model="nomic-embed-text:latest",
        temperature=0.3
    )
    print("✅ Ollama conectado!\n")
except Exception as e:
    print(f"❌ Erro: {e}")
    print("\n💡 Certifique-se que Ollama está rodando:")
    print("   ollama serve")
    sys.exit(1)

print("🔍 Analisando mensagens de teste...\n")
print("="*60)

relevantes = []

for i, msg in enumerate(MENSAGENS_TESTE, 1):
    print(f"\n📨 Mensagem {i}/{len(MENSAGENS_TESTE)}")
    print(f"   @{msg['username']} ({msg['date']})")
    print(f"   \"{msg['texto'][:60]}...\"" if len(msg['texto']) > 60 else f"   \"{msg['texto']}\"")
    print()
    print("   🤔 Analisando com IA...", end=" ", flush=True)
    
    # Análise
    analise = ollama.analyze_message_relevance(msg['texto'], KEYWORDS)
    
    print("✓")
    print(f"   📊 Resultado:")
    print(f"      • Relevante: {analise.get('relevante', False)}")
    print(f"      • Score: {analise.get('score', 0.0):.2f}")
    print(f"      • Tópico: {analise.get('topico_principal', 'N/A')}")
    print(f"      • Resumo: {analise.get('resumo', 'N/A')}")
    
    if analise.get('relevante', False):
        relevantes.append({**msg, 'analise': analise})
        print("   ⭐ MENSAGEM RELEVANTE!")

print("\n" + "="*60)
print(f"\n📊 RESUMO:")
print(f"   Total analisadas: {len(MENSAGENS_TESTE)}")
print(f"   Relevantes: {len(relevantes)}")
print(f"   Taxa: {len(relevantes)/len(MENSAGENS_TESTE)*100:.1f}%")

if relevantes:
    print(f"\n💡 MENSAGENS RELEVANTES:\n")
    for msg in relevantes:
        print(f"   • [@{msg['username']}]: {msg['analise']['resumo']}")
        print(f"     Score: {msg['analise']['score']:.2f}\n")

    # Teste de geração de resumo
    print("="*60)
    print("\n🤖 Gerando resumo com IA...\n")
    
    resumo = ollama.generate_group_summary([
        {
            'username': m['username'],
            'date': m['date'],
            'text': m['texto']
        }
        for m in relevantes
    ])
    
    print(resumo)

print("\n" + "="*60)
print("\n✅ DEMO COMPLETO!")
print("\n💡 Se chegou até aqui, o sistema está funcionando!")
print("   Agora configure suas credenciais do Telegram e rode:")
print("   python3 main.py\n")
