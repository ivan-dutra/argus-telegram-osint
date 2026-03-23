"""
Telegram Monitor Module
Monitora grupos em tempo real e coleta mensagens relevantes
"""

from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, User
from datetime import datetime, timedelta, timezone
import asyncio
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TelegramMonitor:
    def __init__(self, api_id: int, api_hash: str, phone: str, 
                 session_name: str, database, ollama_client, keywords: List[str],
                 relevance_threshold: float = 0.6):
        
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.db = database
        self.ollama = ollama_client
        self.keywords = keywords
        self.relevance_threshold = relevance_threshold
        
        self.client = None
        self.monitored_groups = {}
        self.start_time = datetime.now()
        self.message_count = 0
        self.relevant_count = 0
    
    async def start(self):
        """Inicia o cliente Telegram"""
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        await self.client.start(phone=self.phone)
        logger.info("✓ Telegram conectado")
        
        # Carregar grupos
        await self.load_groups()
        
        # Registrar handler de novas mensagens
        self.client.add_event_handler(
            self.handle_new_message,
            events.NewMessage(chats=list(self.monitored_groups.keys()))
        )
        
        logger.info(f"🔍 Monitorando {len(self.monitored_groups)} grupos")
        logger.info(f"🎯 Keywords: {', '.join(self.keywords)}")
    
    async def load_groups(self):
        """Carrega todos os grupos/canais que o usuário participa"""
        logger.info("📋 Carregando grupos...")
        
        dialogs = await self.client.get_dialogs()
        
        for dialog in dialogs:
            entity = dialog.entity
            
            # Apenas grupos e canais
            if isinstance(entity, (Channel, Chat)):
                group_id = entity.id
                
                self.monitored_groups[group_id] = {
                    'id': group_id,
                    'title': entity.title,
                    'username': getattr(entity, 'username', None),
                    'members_count': getattr(entity, 'participants_count', 0),
                    'is_channel': isinstance(entity, Channel)
                }
                
                # Salvar no banco
                self.db.add_group(self.monitored_groups[group_id])
        
        logger.info(f"✓ {len(self.monitored_groups)} grupos carregados")
    
    async def handle_new_message(self, event):
        """Handler para novas mensagens"""
        try:
            message = event.message
            
            # Ignorar mensagens sem texto
            if not message.text:
                return
            
            # Informações do grupo
            chat = await event.get_chat()
            group_id = chat.id
            group_info = self.monitored_groups.get(group_id, {})
            
            # Informações do usuário
            sender = await event.get_sender()
            username = getattr(sender, 'username', None) or 'unknown'
            user_id = sender.id if sender else 0
            
            self.message_count += 1
            
            # Log básico
            logger.debug(f"📨 [{group_info.get('title', 'Unknown')}] @{username}: {message.text[:50]}...")
            
            # Verificar se contém alguma keyword (filtro rápido)
            text_lower = message.text.lower()
            has_keyword = any(kw.lower() in text_lower for kw in self.keywords)
            
            if not has_keyword:
                return
            
            # Análise com IA
            analysis = self.ollama.analyze_message_relevance(message.text, self.keywords)
            
            if not analysis.get('relevante', False):
                return
            
            score = analysis.get('score', 0.0)
            
            if score < self.relevance_threshold:
                return
            
            # Mensagem relevante!
            self.relevant_count += 1
            
            logger.info(f"⭐ RELEVANTE [{score:.2f}] @{username} em {group_info.get('title')}")
            logger.info(f"   💡 {analysis.get('resumo', '')}")
            
            # Salvar no banco
            message_data = {
                'message_id': message.id,
                'group_id': group_id,
                'group_name': group_info.get('title', 'Unknown'),
                'username': username,
                'user_id': user_id,
                'text': message.text,
                'date': message.date,
                'relevance_score': score,
                'analysis': analysis,
                'keywords_matched': analysis.get('mencoes_importantes', [])
            }
            
            self.db.add_message(message_data)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
    
    async def get_historical_messages(self, hours: int = 8, limit_per_group: int = 100):
        """Busca mensagens históricas de hoje"""#######################################################################################################################
        logger.info(f"📥 Buscando mensagens das últimasss {hours}h...")
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        total_processed = 0
        
        for group_id, group_info in self.monitored_groups.items():
            try:
                logger.info(f"  📂 {group_info['title']}...")
                
                messages = await self.client.get_messages(
                    group_id,
                    limit=limit_per_group
                )
                
                for message in messages:
                    # Apenas mensagens recentes
                    msg_dt = message.date
                    if msg_dt.tzinfo is None:
                        msg_dt = msg_dt.replace(tzinfo=timezone.utc)
                    if msg_dt < cutoff_time:
                        break
                    
                    if not message.text:
                        continue
                    
                    # Filtro rápido de keywords
                    text_lower = message.text.lower()
                    has_keyword = any(kw.lower() in text_lower for kw in self.keywords)
                    
                    if not has_keyword:
                        continue
                    
                    # Análise
                    analysis = self.ollama.analyze_message_relevance(
                        message.text, 
                        self.keywords
                    )
                    
                    if not analysis.get('relevante', False):
                        continue
                    
                    score = analysis.get('score', 0.0)
                    if score < self.relevance_threshold:
                        continue
                    
                    # Salvar
                    sender = await message.get_sender()
                    username = getattr(sender, 'username', None) or 'unknown'
                    
                    message_data = {
                        'message_id': message.id,
                        'group_id': group_id,
                        'group_name': group_info['title'],
                        'username': username,
                        'user_id': sender.id if sender else 0,
                        'text': message.text,
                        'date': message.date,
                        'relevance_score': score,
                        'analysis': analysis,
                        'keywords_matched': analysis.get('mencoes_importantes', [])
                    }
                    
                    self.db.add_message(message_data)
                    total_processed += 1
                
                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao buscar histórico de {group_info['title']}: {e}")
        
        logger.info(f"✓ {total_processed} mensagens relevantes processadas")
        return total_processed
    
    async def run(self):
        """Executa o monitoramento"""
        logger.info("🚀 Iniciando monitoramento...")
        await self.client.run_until_disconnected()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do monitor"""
        uptime = datetime.now() - self.start_time
        
        return {
            'uptime': str(uptime).split('.')[0],
            'groups': len(self.monitored_groups),
            'messages_processed': self.message_count,
            'relevant_messages': self.relevant_count,
            'relevance_rate': f"{(self.relevant_count/self.message_count*100):.1f}%" if self.message_count > 0 else "0%"
        }
