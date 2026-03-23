#!/usr/bin/env python3
"""
Keyword Manager - Gerenciamento dinâmico de keywords e perfis de monitoramento
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
import sys

class KeywordManager:
    def __init__(self, config_path='config/config.yaml', profiles_path='config/profiles.yaml'):
        self.config_path = Path(config_path)
        self.profiles_path = Path(profiles_path)
        self.config = self._load_config()
        self.profiles = self._load_profiles()
    
    def _load_config(self):
        """Carrega configuração principal"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _save_config(self):
        """Salva configuração"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def _load_profiles(self):
        """Carrega perfis de monitoramento"""
        if self.profiles_path.exists():
            with open(self.profiles_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {'profiles': {}}
    
    def _save_profiles(self):
        """Salva perfis"""
        with open(self.profiles_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.profiles, f, allow_unicode=True, default_flow_style=False)
    
    # ===== KEYWORDS =====
    
    def list_keywords(self):
        """Lista keywords ativas"""
        keywords = self.config.get('osint', {}).get('keywords', [])
        print(f"\n📋 KEYWORDS ATIVAS ({len(keywords)}):\n")
        for i, kw in enumerate(keywords, 1):
            print(f"   {i}. {kw}")
        print()
    
    def add_keyword(self, *keywords):
        """Adiciona uma ou mais keywords"""
        current = self.config.get('osint', {}).get('keywords', [])
        added = []
        
        for kw in keywords:
            if kw not in current:
                current.append(kw)
                added.append(kw)
        
        self.config['osint']['keywords'] = current
        self._save_config()
        
        print(f"\n✅ {len(added)} keyword(s) adicionada(s):")
        for kw in added:
            print(f"   + {kw}")
        print()
    
    def remove_keyword(self, *keywords):
        """Remove uma ou mais keywords"""
        current = self.config.get('osint', {}).get('keywords', [])
        removed = []
        
        for kw in keywords:
            if kw in current:
                current.remove(kw)
                removed.append(kw)
        
        self.config['osint']['keywords'] = current
        self._save_config()
        
        print(f"\n✅ {len(removed)} keyword(s) removida(s):")
        for kw in removed:
            print(f"   - {kw}")
        print()
    
    def clear_keywords(self):
        """Remove todas as keywords"""
        self.config['osint']['keywords'] = []
        self._save_config()
        print("\n✅ Todas as keywords foram removidas\n")
    
    # ===== PERFIS =====
    
    def list_profiles(self):
        """Lista perfis disponíveis"""
        profiles = self.profiles.get('profiles', {})
        print(f"\n📁 PERFIS DISPONÍVEIS ({len(profiles)}):\n")
        
        for name, data in profiles.items():
            keywords_count = len(data.get('keywords', []))
            description = data.get('description', 'Sem descrição')
            active = "🟢 ATIVO" if self.get_active_profile() == name else "⚪"
            
            print(f"   {active} {name}")
            print(f"      📝 {description}")
            print(f"      🔑 {keywords_count} keywords")
            print()
    
    def create_profile(self, name, description, *keywords):
        """Cria novo perfil"""
        if 'profiles' not in self.profiles:
            self.profiles['profiles'] = {}
        
        self.profiles['profiles'][name] = {
            'description': description,
            'keywords': list(keywords),
            'created_at': datetime.now().isoformat(),
            'threshold': 0.6
        }
        
        self._save_profiles()
        print(f"\n✅ Perfil '{name}' criado com {len(keywords)} keywords\n")
    
    def delete_profile(self, name):
        """Deleta um perfil"""
        if name in self.profiles.get('profiles', {}):
            del self.profiles['profiles'][name]
            self._save_profiles()
            print(f"\n✅ Perfil '{name}' deletado\n")
        else:
            print(f"\n❌ Perfil '{name}' não encontrado\n")
    
    def activate_profile(self, name):
        """Ativa um perfil"""
        profiles = self.profiles.get('profiles', {})
        
        if name not in profiles:
            print(f"\n❌ Perfil '{name}' não encontrado\n")
            return
        
        # Atualizar keywords no config
        profile_data = profiles[name]
        self.config['osint']['keywords'] = profile_data['keywords']
        self.config['osint']['relevance_threshold'] = profile_data.get('threshold', 0.6)
        
        # Marcar perfil ativo
        if 'active_profile' not in self.config['osint']:
            self.config['osint']['active_profile'] = name
        else:
            self.config['osint']['active_profile'] = name
        
        self._save_config()
        
        keywords_count = len(profile_data['keywords'])
        print(f"\n✅ Perfil '{name}' ATIVADO!")
        print(f"   📝 {profile_data['description']}")
        print(f"   🔑 {keywords_count} keywords carregadas")
        print(f"   📊 Threshold: {profile_data.get('threshold', 0.6)}\n")
    
    def get_active_profile(self):
        """Retorna perfil ativo"""
        return self.config.get('osint', {}).get('active_profile', None)
    
    def add_keyword_to_profile(self, profile_name, *keywords):
        """Adiciona keywords a um perfil"""
        if profile_name not in self.profiles.get('profiles', {}):
            print(f"\n❌ Perfil '{profile_name}' não encontrado\n")
            return
        
        profile = self.profiles['profiles'][profile_name]
        current = profile.get('keywords', [])
        added = []
        
        for kw in keywords:
            if kw not in current:
                current.append(kw)
                added.append(kw)
        
        profile['keywords'] = current
        self._save_profiles()
        
        print(f"\n✅ {len(added)} keyword(s) adicionada(s) ao perfil '{profile_name}':")
        for kw in added:
            print(f"   + {kw}")
        print()
        
        # Se o perfil está ativo, atualizar config também
        if self.get_active_profile() == profile_name:
            self.config['osint']['keywords'] = current
            self._save_config()
            print("   ⚡ Perfil ativo atualizado!")
    
    def export_profile(self, name, filepath):
        """Exporta perfil para arquivo"""
        if name not in self.profiles.get('profiles', {}):
            print(f"\n❌ Perfil '{name}' não encontrado\n")
            return
        
        profile = self.profiles['profiles'][name]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Perfil '{name}' exportado para: {filepath}\n")
    
    def import_profile(self, name, filepath):
        """Importa perfil de arquivo"""
        with open(filepath, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        if 'profiles' not in self.profiles:
            self.profiles['profiles'] = {}
        
        self.profiles['profiles'][name] = profile
        self._save_profiles()
        
        print(f"\n✅ Perfil '{name}' importado de: {filepath}\n")
    
    # ===== THRESHOLD =====
    
    def set_threshold(self, value):
        """Define threshold de relevância"""
        try:
            threshold = float(value)
            if 0 <= threshold <= 1:
                self.config['osint']['relevance_threshold'] = threshold
                self._save_config()
                print(f"\n✅ Threshold definido para: {threshold}\n")
            else:
                print("\n❌ Threshold deve estar entre 0 e 1\n")
        except ValueError:
            print("\n❌ Valor inválido\n")
    
    def get_threshold(self):
        """Mostra threshold atual"""
        threshold = self.config.get('osint', {}).get('relevance_threshold', 0.6)
        print(f"\n📊 Threshold atual: {threshold}")
        print(f"   0.0-0.4: Muito permissivo")
        print(f"   0.5-0.6: Balanceado ⭐")
        print(f"   0.7-0.8: Restritivo")
        print(f"   0.9-1.0: Muito restritivo\n")


def main():
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🔧 KEYWORD MANAGER                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

USO:
  python keyword_manager.py <comando> [argumentos]

COMANDOS - KEYWORDS:
  list                          - Listar keywords ativas
  add <kw1> <kw2> ...          - Adicionar keywords
  remove <kw1> <kw2> ...       - Remover keywords
  clear                         - Remover todas keywords

COMANDOS - PERFIS:
  profiles                      - Listar perfis
  create <nome> <desc> <kw...> - Criar perfil
  activate <nome>               - Ativar perfil
  delete <nome>                 - Deletar perfil
  add-to <perfil> <kw...>      - Adicionar keywords ao perfil
  export <nome> <arquivo>       - Exportar perfil
  import <nome> <arquivo>       - Importar perfil

COMANDOS - THRESHOLD:
  threshold                     - Ver threshold atual
  threshold <valor>             - Definir threshold (0-1)

EXEMPLOS:
  python keyword_manager.py add "bitcoin" "crypto" "nft"
  python keyword_manager.py create carding "Monitorar fraudes" "gg" "bin" "live"
  python keyword_manager.py activate carding
  python keyword_manager.py threshold 0.7
""")
        return
    
    manager = KeywordManager()
    command = sys.argv[1].lower()
    
    # Keywords
    if command == 'list':
        manager.list_keywords()
    
    elif command == 'add':
        if len(sys.argv) < 3:
            print("\n❌ Uso: add <keyword1> <keyword2> ...\n")
        else:
            manager.add_keyword(*sys.argv[2:])
    
    elif command == 'remove':
        if len(sys.argv) < 3:
            print("\n❌ Uso: remove <keyword1> <keyword2> ...\n")
        else:
            manager.remove_keyword(*sys.argv[2:])
    
    elif command == 'clear':
        manager.clear_keywords()
    
    # Perfis
    elif command == 'profiles':
        manager.list_profiles()
    
    elif command == 'create':
        if len(sys.argv) < 5:
            print("\n❌ Uso: create <nome> <descrição> <keyword1> <keyword2> ...\n")
        else:
            manager.create_profile(sys.argv[2], sys.argv[3], *sys.argv[4:])
    
    elif command == 'activate':
        if len(sys.argv) < 3:
            print("\n❌ Uso: activate <nome_perfil>\n")
        else:
            manager.activate_profile(sys.argv[2])
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("\n❌ Uso: delete <nome_perfil>\n")
        else:
            manager.delete_profile(sys.argv[2])
    
    elif command == 'add-to':
        if len(sys.argv) < 4:
            print("\n❌ Uso: add-to <perfil> <keyword1> <keyword2> ...\n")
        else:
            manager.add_keyword_to_profile(sys.argv[2], *sys.argv[3:])
    
    elif command == 'export':
        if len(sys.argv) < 4:
            print("\n❌ Uso: export <nome_perfil> <arquivo.json>\n")
        else:
            manager.export_profile(sys.argv[2], sys.argv[3])
    
    elif command == 'import':
        if len(sys.argv) < 4:
            print("\n❌ Uso: import <nome_perfil> <arquivo.json>\n")
        else:
            manager.import_profile(sys.argv[2], sys.argv[3])
    
    # Threshold
    elif command == 'threshold':
        if len(sys.argv) == 2:
            manager.get_threshold()
        else:
            manager.set_threshold(sys.argv[2])
    
    else:
        print(f"\n❌ Comando desconhecido: {command}\n")


if __name__ == '__main__':
    main()
