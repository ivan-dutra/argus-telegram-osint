"""
Report Generator Module
Gera relatórios OSINT baseados nas mensagens coletadas
"""

from datetime import datetime
from typing import List, Dict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, database, ollama_client, output_dir: str):
        self.db = database
        self.ollama = ollama_client
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(self, keywords: List[str] = None) -> str:
        """Gera relatório diário completo"""
        logger.info("📊 Gerando relatório diário...")
        
        report_date = datetime.now().strftime("%Y-%m-%d")
        
        # Estatísticas gerais
        stats = self.db.get_statistics()
        
        # Mensagens relevantes de hoje
        messages = self.db.get_today_messages(min_relevance=0.6)
        
        # Agrupar por grupo
        messages_by_group = {}
        for msg in messages:
            group_name = msg['group_name']
            if group_name not in messages_by_group:
                messages_by_group[group_name] = []
            messages_by_group[group_name].append(msg)
        
        # Começar relatório
        taxa_relevancia = (stats['relevant_today']/stats['today_messages']*100) if stats['today_messages'] > 0 else 0
        
        report = f"""# 🔍 RELATÓRIO OSINT - {report_date}

## 📈 ESTATÍSTICAS GERAIS

- **Total de Mensagens Processadas**: {stats['today_messages']:,}
- **Mensagens Relevantes**: {stats['relevant_today']:,}
- **Grupos Monitorados**: {stats['active_groups']}
- **Taxa de Relevância**: {taxa_relevancia:.1f}%

---

"""
        
        # Análise por grupo
        if messages_by_group:
            report += "## 📱 ANÁLISE POR GRUPO\n\n"
            
            for group_name, group_messages in messages_by_group.items():
                report += f"### 🔸 {group_name}\n\n"
                report += f"**Mensagens relevantes**: {len(group_messages)}\n\n"
                
                # Gerar resumo do grupo com IA
                summary = self.ollama.generate_group_summary(group_messages)
                report += f"{summary}\n\n"
                
                # Top 5 mensagens mais relevantes
                top_messages = sorted(
                    group_messages, 
                    key=lambda x: x['relevance_score'], 
                    reverse=True
                )[:5]
                
                if top_messages:
                    report += "**🔥 Destaques**:\n\n"
                    for msg in top_messages:
                        # Converter date para string se necessário
                        msg_date = msg['date']
                        if isinstance(msg_date, str):
                            date_str = msg_date
                        else:
                            date_str = msg_date.strftime('%H:%M')
                        
                        report += f"- **[@{msg['username']}]** ({date_str}): "
                        report += f"{msg['analysis'].get('resumo', msg['text'][:100])}\n"
                        report += f"  *Score: {msg['relevance_score']:.2f}*\n\n"
                
                report += "---\n\n"
        
        # Análise cruzada
        if len(messages_by_group) > 1:
            report += "## 🔗 ANÁLISE CRUZADA\n\n"
            cross_analysis = self.ollama.cross_reference_analysis(messages_by_group)
            report += f"{cross_analysis}\n\n"
            report += "---\n\n"
        
        # Análise por keywords
        if keywords:
            report += "## 🎯 ANÁLISE POR PALAVRA-CHAVE\n\n"
            
            for keyword in keywords:
                keyword_msgs = self.db.get_messages_by_keyword(keyword, days=1)
                
                if keyword_msgs:
                    report += f"### 🔎 \"{keyword}\" - {len(keyword_msgs)} menções\n\n"
                    
                    # Agrupar por usuário
                    users = {}
                    for msg in keyword_msgs:
                        username = msg['username']
                        if username not in users:
                            users[username] = []
                        users[username].append(msg)
                    
                    report += f"**Usuários únicos**: {len(users)}\n\n"
                    
                    # Top usuários
                    top_users = sorted(users.items(), key=lambda x: len(x[1]), reverse=True)[:5]
                    
                    for username, user_msgs in top_users:
                        report += f"- **@{username}**: {len(user_msgs)} menções\n"
                        # Primeira mensagem como exemplo
                        example = user_msgs[0]
                        report += f"  *\"{example['analysis'].get('resumo', example['text'][:80])}...\"*\n\n"
                    
                    report += "\n"
        
        # Rodapé
        report += f"""---

**Relatório gerado em**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Sistema**: Telegram OSINT Bot v1.0
"""
        
        # Salvar arquivo
        filename = f"relatorio_{report_date}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ Relatório salvo: {filepath}")
        
        # Salvar no banco
        self.db.save_report({
            'date': datetime.now().date(),
            'type': 'daily',
            'content': report,
            'keywords': keywords or [],
            'groups_count': len(messages_by_group),
            'messages_count': len(messages)
        })
        
        return report
    
    def generate_keyword_report(self, keyword: str, days: int = 24) -> str:
        """Gera relatório focado em uma palavra-chave específica"""
        logger.info(f"🔍 Gerando relatório para keyword: {keyword}")
        ############################################################################################################################################
        
        messages = self.db.get_messages_by_keyword(keyword, days=days)
        
        if not messages:
            return f"Nenhuma mensagem encontrada para '{keyword}' nos últimos {days} dia(s)."
        
        report = f"""# 🎯 RELATÓRIO: "{keyword}"

**Período**: Últimos {days} dia(s)
**Total de menções**: {len(messages)}

---

## 📊 ANÁLISE

"""
        
        # Agrupar por grupo
        by_group = {}
        for msg in messages:
            group = msg['group_name']
            if group not in by_group:
                by_group[group] = []
            by_group[group].append(msg)
        
        report += f"**Grupos com menções**: {len(by_group)}\n\n"
        
        for group, msgs in sorted(by_group.items(), key=lambda x: len(x[1]), reverse=True):
            report += f"### {group} ({len(msgs)} menções)\n\n"
            
            # Top 3 mais relevantes
            top = sorted(msgs, key=lambda x: x['relevance_score'], reverse=True)[:3]
            
            for msg in top:
                # Converter date
                msg_date = msg['date']
                if isinstance(msg_date, str):
                    date_str = msg_date
                else:
                    date_str = msg_date.strftime('%d/%m %H:%M')
                
                report += f"- [@{msg['username']}] ({date_str})\n"
                report += f"  {msg['analysis'].get('resumo', msg['text'][:100])}\n"
                report += f"  *Score: {msg['relevance_score']:.2f}*\n\n"
        
        # Usuários mais ativos
        users = {}
        for msg in messages:
            username = msg['username']
            users[username] = users.get(username, 0) + 1
        
        report += "\n## 👥 USUÁRIOS MAIS ATIVOS\n\n"
        
        top_users = sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]
        for username, count in top_users:
            report += f"- @{username}: {count} menções\n"
        
        report += f"\n---\n\n**Gerado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Salvar
        filename = f"keyword_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✓ Relatório de keyword salvo: {filepath}")
        
        return report
    
    def generate_user_report(self, username: str, days: int = 7) -> str:
        """Gera relatório focado em um usuário específico"""
        logger.info(f"👤 Gerando relatório para usuário: @{username}")
        
        # Buscar mensagens do usuário
        messages = self.db.get_today_messages()
        user_messages = [m for m in messages if m['username'] == username]
        
        if not user_messages:
            return f"Nenhuma atividade relevante de @{username} encontrada."
        
        report = f"""# 👤 PERFIL OSINT: @{username}

**Período analisado**: Últimos {days} dia(s)
**Mensagens relevantes**: {len(user_messages)}

---

## 📱 ATIVIDADE POR GRUPO

"""
        
        by_group = {}
        for msg in user_messages:
            group = msg['group_name']
            if group not in by_group:
                by_group[group] = []
            by_group[group].append(msg)
        
        for group, msgs in sorted(by_group.items(), key=lambda x: len(x[1]), reverse=True):
            report += f"### {group}\n\n"
            report += f"**Mensagens**: {len(msgs)}\n\n"
            
            for msg in msgs[:5]:  # Top 5
                # Converter date para string
                msg_date = msg['date']
                if isinstance(msg_date, str):
                    date_str = msg_date
                else:
                    date_str = msg_date.strftime('%d/%m %H:%M')
                
                report += f"- ({date_str}): "
                report += f"{msg['analysis'].get('resumo', msg['text'][:100])}\n"
        
        report += f"\n---\n\n**Gerado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return report
