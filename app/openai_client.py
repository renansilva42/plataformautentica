import os
import requests
import json
import base64
from io import BytesIO
from flask import current_app

class OpenAIManager:
    """Classe para gerenciar chamadas à API do OpenAI"""
    
    @staticmethod
    def analyze_instagram_images(bio_image, profile_image, feed_image):
        """
        Analisa imagens do Instagram usando a API do OpenAI
        
        Args:
            bio_image: Imagem da bio do Instagram
            profile_image: Imagem do perfil do Instagram
            feed_image: Imagem do feed do Instagram
            
        Returns:
            tuple: (success, result)
        """
        try:
            # URL do endpoint - CORRIGIDO: endpoint correto para API de chat com imagens
            url = "https://api.openai.com/v1/chat/completions"
            
            # Obtém a chave da API do ambiente
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                return False, "API key não configurada"
            
            # Cabeçalhos da requisição
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Converter imagens para URLs base64
            def image_to_base64_url(image):
                image_data = BytesIO(image.read())
                image.seek(0)  # Reset file pointer
                base64_encoded = base64.b64encode(image_data.getvalue()).decode('utf-8')
                return f"data:image/jpeg;base64,{base64_encoded}"
            
            try:
                bio_image_url = image_to_base64_url(bio_image)
                profile_image_url = image_to_base64_url(profile_image)
                feed_image_url = image_to_base64_url(feed_image)
            except Exception as e:
                current_app.logger.error(f"Erro ao processar imagens: {str(e)}")
                return False, f"Erro ao processar as imagens: {str(e)}"
            
            # Corpo da requisição (JSON) - CORRIGIDO: formato correto para chat completions
            payload = {
                "model": "gpt-4.1",  # Modelo com suporte a visão
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "system",
                        "content": """
                        Você é um analista arquetípico altamente capacitado, treinado nos conceitos profundos dos livros de Carl Jung. Sua tarefa é realizar uma análise de microprocessos para complementar o diagnóstico arquetípico, utilizando microfiltros e um esquema de pontuação refinado.
                        
                        Utilize os conhecimentos dos seguintes livros:
                        1. Os Arquétipos e o Inconsciente Coletivo
                        2. O Homem e Seus Símbolos
                        3. Aion: Estudos sobre o Simbolismo do Si-mesmo
                        4. Tipos Psicológicos
                        """
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
                                🧩 Analise estas imagens do perfil do Instagram com base na metodologia arquetípica:
                                
                                1. MICROFILTROS ARQUETÍPICOS
                                a) Luz ou Sombra do Arquétipo
                                b) Linguagem Textual – Emocional ou Racional
                                c) Estética Visual – Ativa ou Receptiva
                                
                                2. ESQUEMA DE PONTUAÇÃO (0-5)
                                a) Força Arquetípica
                                b) Coerência (Imagem x Texto x Energia)
                                c) Alinhamento com o Público-Alvo
                                
                                Produza um relatório completo com análise e recomendações.
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": bio_image_url,
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": profile_image_url,
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": feed_image_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Log para debug
            current_app.logger.info(f"Enviando requisição para OpenAI API: {url}")
            
            # Enviar a requisição POST
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # Verificar o status da resposta
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Extrair o conteúdo da análise da resposta
                    analysis_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    if not analysis_text:
                        current_app.logger.error(f"Resposta vazia da API: {json.dumps(result)}")
                        return False, "Resposta vazia da API"
                    
                    return True, analysis_text
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    current_app.logger.error(f"Erro ao processar resposta da API: {str(e)}")
                    return False, f"Erro ao processar resposta da API: {str(e)}"
            else:
                error_msg = f"Erro na requisição: {response.status_code}"
                try:
                    error_details = response.json()
                    current_app.logger.error(f"{error_msg} - {json.dumps(error_details)}")
                    if 'error' in error_details:
                        error_msg += f" - {error_details['error']['message']}"
                except:
                    current_app.logger.error(f"{error_msg} - {response.text}")
                    error_msg += f" - {response.text}"
                
                return False, error_msg
                
        except requests.exceptions.Timeout:
            current_app.logger.error("Timeout ao conectar com a API do OpenAI")
            return False, "Tempo limite excedido ao conectar com o serviço de análise. Tente novamente."
        except requests.exceptions.ConnectionError:
            current_app.logger.error("Erro de conexão com a API do OpenAI")
            return False, "Erro de conexão com o serviço de análise. Verifique sua conexão com a internet."
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f"Erro ao analisar imagens: {error_details}")
            return False, f"Erro ao analisar as imagens: {str(e)}"