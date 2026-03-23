#!/usr/bin/env python3
"""
Telegram OSINT Bot
Sistema de monitoramento e análise em tempo real de grupos do Telegram
"""

import asyncio
import yaml
import logging
from pathlib import Path
from datetime import datetime
import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar stdout/stderr para UTF-8 (Windows cp1252 causa erro com emojis)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
except Exception:
    pass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/osint.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# Imports dos módulos
from src.database import OSINTDatabase
from src.ollama_client import OllamaClient
from src.telegram_monitor import TelegramMonitor
from src.report_generator import ReportGenerator


class OSINTBot:
    def __init__(self, config_path: str = 'config/config.yaml'):
        """Inicializa o bot OSINT"""
        
        # Carregar configurações
        logger.info("🔧 Carregando configurações...")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Inicializar componentes
        logger.info("🗄️ Inicializando banco de dados...")
        self.db = OSINTDatabase(self.config['database']['path'])
        
        logger.info("🤖 Conectando ao Ollama...")
        self.ollama = OllamaClient(
            base_url=self.config['ollama']['base_url'],
            model=self.config['ollama']['model'],
            embedding_model=self.config['ollama']['embedding_model'],
            temperature=self.config['ollama']['temperature'],
            top_p=self.config['ollama']['top_p'],
            max_tokens=self.config['ollama']['max_tokens']
        )
        
        logger.info("📱 Inicializando monitor do Telegram...")
        self.monitor = TelegramMonitor(
            api_id=self.config['telegram']['api_id'],
            api_hash=self.config['telegram']['api_hash'],
            phone=self.config['telegram']['phone'],
            session_name=self.config['telegram']['session_name'],
            database=self.db,
            ollama_client=self.ollama,
            keywords=self.config['osint']['keywords'],
            relevance_threshold=self.config['osint']['relevance_threshold']
        )
        
        logger.info("📊 Inicializando gerador de relatórios...")
        self.report_gen = ReportGenerator(
            database=self.db,
            ollama_client=self.ollama,
            output_dir=self.config['reports']['output_dir']
        )
        
        logger.info("✅ Todos os componentes inicializados!")
    
    async def start_monitoring(self):
        """Inicia o monitoramento"""
        try:
            # Conectar ao Telegram
            await self.monitor.start()
            
            # Buscar mensagens históricas de hoje
            logger.info("📥 Coletando mensagens de hoje...")
            await self.monitor.get_historical_messages(hours=1)
            
            # Estatísticas iniciais
            stats = self.db.get_statistics()
            logger.info(f"""
╔══════════════════════════════════════════════════════════
║ 📊 ESTATÍSTICAS INICIAIS
║ 
║ • Total de mensagens: {stats['total_messages']:,}
║ • Mensagens hoje: {stats['today_messages']:,}
║ • Mensagens relevantes: {stats['relevant_today']:,}
║ • Grupos ativos: {stats['active_groups']}
╚══════════════════════════════════════════════════════════
""")
            
            # Iniciar monitoramento em tempo real
            logger.info("🚀 Monitoramento em tempo real ATIVO!")
            logger.info("Pressione Ctrl+C para parar")
            
            # Agendar relatório periódico
            asyncio.create_task(self.periodic_report())
            
            # Manter rodando
            await self.monitor.run()
            
        except KeyboardInterrupt:
            logger.info("\n⏹️ Parando monitoramento...")
            await self.stop()
        except Exception as e:
            logger.error(f"❌ Erro crítico: {e}", exc_info=True)
            await self.stop()
    
    async def periodic_report(self):
        """Gera relatórios periódicos"""
        while True:
            try:
                # Aguardar 1 hora
                await asyncio.sleep(3600)
                
                logger.info("⏰ Gerando relatório periódico...")
                
                # Gerar relatório
                report = self.report_gen.generate_daily_report(
                    keywords=self.config['osint']['keywords']
                )
                
                # Estatísticas do monitor
                monitor_stats = self.monitor.get_stats()
                logger.info(f"""
╔══════════════════════════════════════════════════════════
║ 🔄 RELATÓRIO PERIÓDICO
║ 
║ Uptime: {monitor_stats['uptime']}
║ Mensagens processadas: {monitor_stats['messages_processed']:,}
║ Mensagens relevantes: {monitor_stats['relevant_messages']:,}
║ Taxa de relevância: {monitor_stats['relevance_rate']}
╚══════════════════════════════════════════════════════════
""")
                
            except Exception as e:
                logger.error(f"Erro no relatório periódico: {e}")
    
    async def stop(self):
        """Para o bot e faz cleanup"""
        logger.info("🧹 Limpando recursos...")
        
        # Gerar relatório final
        logger.info("📊 Gerando relatório final...")
        try:
            self.report_gen.generate_daily_report(
                keywords=self.config['osint']['keywords']
            )
        except Exception as e:
            logger.error(f"Erro ao gerar relatório final: {e}")
        
        # Cleanup de dados antigos
        if self.config['osint']['store_history']:
            days = self.config['osint']['history_days']
            self.db.cleanup_old_data(days=days)
        
        logger.info("✅ Bot encerrado")
    
    async def generate_report_now(self):
        """Gera relatório imediato (modo comando)"""
        logger.info("📊 Gerando relatório...")
        
        report = self.report_gen.generate_daily_report(
            keywords=self.config['osint']['keywords']
        )
        
        print("\n" + "="*60)
        print(report)
        print("="*60 + "\n")
    
    async def search_keyword(self, keyword: str, days: int = 7):
        """Busca por palavra-chave específica""" 
        logger.info(f"🔍 Buscando: {keyword}")
        
        report = self.report_gen.generate_keyword_report(keyword, days=days)
        
        print("\n" + "="*60)
        print(report)
        print("="*60 + "\n")


async def main():
    """Função principal"""
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🔍 TELEGRAM OSINT BOT v1.0                      ║
║         Powered by @ivm4nsec                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Criar diretórios
    Path('logs').mkdir(exist_ok=True)
    Path('data/reports').mkdir(parents=True, exist_ok=True)
    
    # Verificar se config existe
    if not Path('config/config.yaml').exists():
        logger.error("❌ Arquivo config/config.yaml não encontrado!")
        logger.info("📝 Configure suas credenciais do Telegram no arquivo config/config.yaml")
        return
    
    # Inicializar bot
    try:
        bot = OSINTBot()
        
        # Verificar argumentos
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'report':
                # Gerar relatório apenas
                await bot.generate_report_now()
            
            elif command == 'search':
                if len(sys.argv) < 3:
                    print("Uso: python main.py search <keyword> [dias]")
                    return
                
                keyword = sys.argv[2]
                days = int(sys.argv[3]) if len(sys.argv) > 3 else 1
                await bot.search_keyword(keyword, days)
            
            else:
                print(f"Comando desconhecido: {command}")
                print("\nComandos disponíveis:")
                print("  python main.py              - Inicia monitoramento em tempo real")
                print("  python main.py report       - Gera relatório imediato")
                print("  python main.py search <kw>  - Busca por palavra-chave")
        
        else:
            # Modo normal: monitoramento contínuo
            await bot.start_monitoring()
    
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar bot: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Até logo!")
