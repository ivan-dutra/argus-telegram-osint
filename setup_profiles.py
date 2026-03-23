#!/usr/bin/env python3
"""
Setup Interativo de Perfis
"""

import yaml
from pathlib import Path

def setup_wizard():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🎯 SETUP DE PERFIS - WIZARD                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

Vamos configurar seu primeiro perfil de monitoramento!

""")
    
    # Escolher tipo
    print("📋 Escolha o tipo de monitoramento:\n")
    print("1. 🔒 Segurança/Fraudes (carding, vazamentos)")
    print("2. 💰 Finanças (crypto, investimentos)")
    print("3. 💼 Trabalho (vagas, freelas)")
    print("4. 🎮 Entretenimento (games, streaming)")
    print("5. 🛍️ E-commerce (vendas, produtos)")
    print("6. 📱 Tecnologia (dev, programação)")
    print("7. ✏️ Customizado (criar do zero)")
    print()
    
    choice = input("Escolha (1-7): ").strip()
    
    profiles_map = {
        '1': ['carding', 'vazamentos', 'infosec'],
        '2': ['crypto', 'investimentos'],
        '3': ['empregos'],
        '4': ['gaming'],
        '5': ['ecommerce', 'marketing'],
        '6': ['tech']
    }
    
    if choice in profiles_map:
        print(f"\n✅ Perfis sugeridos: {', '.join(profiles_map[choice])}")
        profile = profiles_map[choice][0]
        print(f"   Ativando: {profile}\n")
        
        # Ativar perfil
        import subprocess
        subprocess.run(['python', 'keyword_manager.py', 'activate', profile])
        
    elif choice == '7':
        # Criar customizado
        print("\n📝 Criar perfil customizado:")
        name = input("Nome do perfil: ").strip()
        desc = input("Descrição: ").strip()
        print("\nAdicione keywords (uma por linha, vazio para finalizar):")
        
        keywords = []
        while True:
            kw = input("  → ").strip()
            if not kw:
                break
            keywords.append(kw)
        
        if keywords:
            import subprocess
            cmd = ['python', 'keyword_manager.py', 'create', name, desc] + keywords
            subprocess.run(cmd)
            
            print(f"\n✅ Perfil '{name}' criado!")
            activate = input("\nAtivar agora? (s/n): ").strip().lower()
            
            if activate == 's':
                subprocess.run(['python', 'keyword_manager.py', 'activate', name])
    
    else:
        print("\n❌ Opção inválida!")
        return
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         ✅ SETUP CONCLUÍDO!                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

Próximos passos:

1. Ver keywords ativas:
   python keyword_manager.py list

2. Adicionar mais keywords:
   python keyword_manager.py add "nova" "keyword"

3. Iniciar monitoramento:
   python main.py

4. Ver guia completo:
   notepad PERFIS.md

""")

if __name__ == '__main__':
    setup_wizard()
