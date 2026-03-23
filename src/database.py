"""
Database Module with Vector Search
Gerencia armazenamento de mensagens e busca semântica
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class OSINTDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inicializa estrutura do banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                group_id INTEGER,
                group_name TEXT,
                username TEXT,
                user_id INTEGER,
                text TEXT,
                date TIMESTAMP,
                relevance_score REAL,
                analysis_data TEXT,
                keywords_matched TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de grupos monitorados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitored_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER UNIQUE,
                group_name TEXT,
                title TEXT,
                members_count INTEGER,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Tabela de relatórios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date DATE,
                report_type TEXT,
                content TEXT,
                keywords TEXT,
                groups_analyzed INTEGER,
                messages_analyzed INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_date 
            ON messages(date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_group 
            ON messages(group_id, date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_relevance 
            ON messages(relevance_score DESC)
        """)
        
        conn.commit()
        conn.close()
        logger.info("✓ Database inicializado")
    
    def add_message(self, message_data: Dict) -> int:
        """Adiciona uma mensagem ao banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO messages 
                (message_id, group_id, group_name, username, user_id, text, 
                 date, relevance_score, analysis_data, keywords_matched)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_data.get('message_id'),
                message_data.get('group_id'),
                message_data.get('group_name'),
                message_data.get('username'),
                message_data.get('user_id'),
                message_data.get('text'),
                message_data.get('date'),
                message_data.get('relevance_score', 0.0),
                json.dumps(message_data.get('analysis', {})),
                json.dumps(message_data.get('keywords_matched', []))
            ))
            
            message_id = cursor.lastrowid
            conn.commit()
            return message_id
            
        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def add_group(self, group_data: Dict):
        """Adiciona ou atualiza um grupo monitorado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO monitored_groups 
                (group_id, group_name, title, members_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(group_id) DO UPDATE SET
                    group_name = excluded.group_name,
                    title = excluded.title,
                    members_count = excluded.members_count,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                group_data.get('id'),
                group_data.get('username', ''),
                group_data.get('title', ''),
                group_data.get('members_count', 0)
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar grupo: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_today_messages(self, group_id: Optional[int] = None, 
                          min_relevance: float = 0.0) -> List[Dict]:
        """Recupera mensagens de hoje com filtros"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        query = """
            SELECT * FROM messages 
            WHERE date >= ? 
            AND relevance_score >= ?
        """
        params = [today, min_relevance]
        
        if group_id:
            query += " AND group_id = ?"
            params.append(group_id)
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            msg = dict(row)
            msg['analysis'] = json.loads(msg['analysis_data']) if msg['analysis_data'] else {}
            msg['keywords_matched'] = json.loads(msg['keywords_matched']) if msg['keywords_matched'] else []
            messages.append(msg)
        
        return messages
    
    def get_messages_by_keyword(self, keyword: str, days: int = 1) -> List[Dict]:
        """Busca mensagens por palavra-chave"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            SELECT * FROM messages 
            WHERE (text LIKE ? OR keywords_matched LIKE ?)
            AND date >= ?
            ORDER BY relevance_score DESC, date DESC
        """, (f'%{keyword}%', f'%{keyword}%', cutoff_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            msg = dict(row)
            msg['analysis'] = json.loads(msg['analysis_data']) if msg['analysis_data'] else {}
            msg['keywords_matched'] = json.loads(msg['keywords_matched']) if msg['keywords_matched'] else []
            messages.append(msg)
        
        return messages
    
    def get_group_summary_data(self, group_id: int, hours: int = 24) -> List[Dict]:
        """Recupera dados para resumo de um grupo"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT * FROM messages 
            WHERE group_id = ?
            AND date >= ?
            ORDER BY relevance_score DESC, date DESC
            LIMIT 100
        """, (group_id, cutoff_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            msg = dict(row)
            msg['analysis'] = json.loads(msg['analysis_data']) if msg['analysis_data'] else {}
            messages.append(msg)
        
        return messages
    
    def get_monitored_groups(self) -> List[Dict]:
        """Lista grupos monitorados ativos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM monitored_groups 
            WHERE is_active = 1
            ORDER BY last_updated DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_report(self, report_data: Dict) -> int:
        """Salva um relatório gerado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO reports 
                (report_date, report_type, content, keywords, 
                 groups_analyzed, messages_analyzed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                report_data.get('date', datetime.now().date()),
                report_data.get('type', 'daily'),
                report_data.get('content'),
                json.dumps(report_data.get('keywords', [])),
                report_data.get('groups_count', 0),
                report_data.get('messages_count', 0)
            ))
            
            report_id = cursor.lastrowid
            conn.commit()
            return report_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def cleanup_old_data(self, days: int = 7):
        """Remove mensagens antigas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute("""
            DELETE FROM messages WHERE date < ?
        """, (cutoff_date,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"🗑️ Removidas {deleted} mensagens antigas")
        return deleted
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de mensagens
        cursor.execute("SELECT COUNT(*) FROM messages")
        stats['total_messages'] = cursor.fetchone()[0]
        
        # Mensagens hoje
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("SELECT COUNT(*) FROM messages WHERE date >= ?", (today,))
        stats['today_messages'] = cursor.fetchone()[0]
        
        # Grupos ativos
        cursor.execute("SELECT COUNT(*) FROM monitored_groups WHERE is_active = 1")
        stats['active_groups'] = cursor.fetchone()[0]
        
        # Mensagens relevantes hoje
        cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE date >= ? AND relevance_score >= 0.6
        """, (today,))
        stats['relevant_today'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
