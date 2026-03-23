"""
Ollama Integration Module
Gerencia conexão e interações com modelos Ollama locais
"""

import requests
import json
from typing import List, Dict, Optional
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str, model: str, embedding_model: str, **kwargs):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.embedding_model = embedding_model
        self.temperature = kwargs.get('temperature', 0.3)
        self.top_p = kwargs.get('top_p', 0.9)
        self.max_tokens = kwargs.get('max_tokens', 2048)
        
        # Carregar glossário de arquivo
        self.glossario = self._load_glossario()
        
        # Verificar se Ollama está rodando
        self._check_connection()
    
    def _load_glossario(self) -> Dict:
        """Carrega glossário de gírias do arquivo YAML"""
        glossario_path = Path('config/glossario.yaml')
        
        # Glossário padrão (fallback)
        default_glossario = {
            "gg": "cartões gerados/clonados (gift cards fraudulentos)",
            "bin": "primeiros 6 dígitos do cartão (identifica banco/bandeira)",
            "live": "cartão válido/ativo que está funcionando",
            "die": "cartão inválido/bloqueado",
            "cvv": "código de segurança do cartão",
            "drop": "endereço de entrega para receber compras fraudulentas",
            "fullz": "dados completos (nome, CPF, endereço, cartão)",
            "checker": "ferramenta para testar se cartão está ativo",
            "carding": "uso fraudulento de cartões",
            "cc": "credit card (cartão de crédito)",
            "aprovando": "cartão está passando/funcionando",
            "passando": "cartão está sendo aceito em compras",
            "trampo": "trabalho/oportunidade (geralmente ilegal)",
            "método": "técnica específica de fraude",
            "store": "loja online alvo",
            "hit": "sucesso em fraude/compra aprovada"
        }
        
        try:
            if glossario_path.exists():
                with open(glossario_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    glossario = config.get('glossario', {})
                    logger.info(f"✓ Glossário carregado: {len(glossario)} termos")
                    return glossario
            else:
                logger.warning("Glossário não encontrado, usando padrão")
                return default_glossario
        except Exception as e:
            logger.error(f"Erro ao carregar glossário: {e}")
            return default_glossario
    
    def _check_connection(self):
        """Verifica se Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info(f"✓ Ollama conectado. Modelos disponíveis: {len(models)}")
                return True
        except Exception as e:
            logger.error(f"✗ Erro ao conectar com Ollama: {e}")
            logger.error("Certifique-se que Ollama está rodando: ollama serve")
            raise ConnectionError("Ollama não está disponível")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Gera texto usando o modelo"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_predict": self.max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Erro na geração: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro ao gerar texto: {e}")
            return ""
    
    def get_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        try:
            payload = {
                "model": self.embedding_model,
                "prompt": text
            }
            
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embedding', [])
            else:
                logger.error(f"Erro ao gerar embedding: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    def analyze_message_relevance(self, message: str, keywords: List[str]) -> Dict:
        """Analisa relevância de uma mensagem baseado em keywords"""
        
        keywords_str = ", ".join(keywords)
        
        # Criar contexto com glossário
        glossario_texto = "\n".join([f"- {termo}: {definicao}" for termo, definicao in self.glossario.items()])
        
        system_prompt = f"""Você é um analista OSINT especializado em carding e fraudes financeiras.
Você entende as gírias específicas deste contexto:

GLOSSÁRIO:
{glossario_texto}

Seja objetivo e direto. Responda APENAS em JSON válido sem markdown.
Use o glossário para interpretar corretamente as mensagens."""
        
        prompt = f"""Analise esta mensagem de Telegram e determine se é relevante para as palavras-chave: {keywords_str}

MENSAGEM:
{message}

Retorne APENAS um JSON com:
{{
    "relevante": true/false,
    "score": 0.0-1.0,
    "topico_principal": "string",
    "resumo": "string curto explicando o contexto (máx 100 chars)",
    "mencoes_importantes": ["array", "de", "termos", "do", "glossario"],
    "tipo_atividade": "venda|compra|método|informação|outros"
}}"""

        response = self.generate(prompt, system_prompt)
        
        try:
            # Limpar possível markdown
            response = response.strip()
            if response.startswith('```'):
                response = response.split('```')[1]
                if response.startswith('json'):
                    response = response[4:]
            
            result = json.loads(response.strip())
            return result
        except json.JSONDecodeError:
            logger.warning(f"Falha ao parsear JSON da análise: {response[:100]}")
            return {
                "relevante": False,
                "score": 0.0,
                "topico_principal": "erro",
                "resumo": "Erro ao analisar",
                "mencoes_importantes": []
            }
    
    def generate_group_summary(self, messages: List[Dict]) -> str:
        """Gera resumo de mensagens de um grupo"""
        
        if not messages:
            return "Nenhuma mensagem relevante encontrada."
        
        # Preparar contexto
        context = "\n\n".join([
            f"[@{msg.get('username', 'unknown')}] ({msg.get('date', '')}): {msg.get('text', '')}"
            for msg in messages[:20]  # Limitar para não sobrecarregar
        ])
        
        # Glossário para contexto
        glossario_texto = "\n".join([f"- {termo}: {definicao}" for termo, definicao in self.glossario.items()])
        
        system_prompt = f"""Você é um analista OSINT especializado em carding e fraudes financeiras.
Use este glossário para interpretar as mensagens:

{glossario_texto}

Foque nos FATOS, USUÁRIOS mencionados e INFORMAÇÕES relevantes.
Seja direto e objetivo."""
        
        prompt = f"""Com base nestas mensagens de Telegram, crie um resumo OSINT:

{context}

Estruture assim:
📊 RESUMO DO GRUPO
- Principais atividades (vendas, métodos, discussões)
- BINs/Cartões mencionados
- Valores e preços
- Usuários mais ativos
- Sites/Lojas alvos mencionados
- Métodos ou técnicas discutidas

Seja conciso e focado em INTELIGÊNCIA ACIONÁVEL."""

        return self.generate(prompt, system_prompt)
    
    def cross_reference_analysis(self, group_summaries: Dict[str, List[Dict]]) -> str:
        """Análise cruzada entre múltiplos grupos"""
        
        if not group_summaries:
            return "Nenhum dado para análise cruzada."
        
        context = ""
        for group_name, messages in group_summaries.items():
            context += f"\n\n=== GRUPO: {group_name} ===\n"
            context += "\n".join([
                f"[@{msg.get('username')}]: {msg.get('resumo', msg.get('text', ''))[:100]}"
                for msg in messages[:10]
            ])
        
        system_prompt = """Você é um analista OSINT especializado em correlacionar informações.
Identifique CONEXÕES, PADRÕES e INSIGHTS entre diferentes fontes."""
        
        prompt = f"""Analise estas informações de MÚLTIPLOS grupos do Telegram:

{context}

Forneça uma análise cruzada identificando:
1. 🔗 Conexões entre grupos
2. 👥 Usuários que aparecem em múltiplos grupos
3. 📈 Padrões e tendências
4. ⚠️ Informações críticas ou alertas
5. 💡 Insights relevantes

Seja objetivo e focado em INTELIGÊNCIA ACIONÁVEL."""

        return self.generate(prompt, system_prompt)
