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
            # URL do endpoint
            url = "https://api.openai.com/v1/responses"
            
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
            
            bio_image_url = image_to_base64_url(bio_image)
            profile_image_url = image_to_base64_url(profile_image)
            feed_image_url = image_to_base64_url(feed_image)
            
            # Corpo da requisição (JSON)
            payload = {
                "model": "gpt-4.1",
                "instructions": """
                🧩 Prompt para Microprocessos e Micrometodologias Arquetípicas

                Contexto: Você é um analista arquetípico altamente capacitado, treinado nos conceitos profundos dos livros de Carl Jung, e possui acesso a imagens e textos dos perfis analisados. Sua tarefa é realizar uma análise de microprocessos para complementar o diagnóstico arquetípico, utilizando microfiltros e um esquema de pontuação refinado.

                Objetivo: Validar rapidamente a presença e intensidade dos arquétipos manifestados e a coerência entre os elementos visuais e textuais, além de identificar o potencial alinhamento com o público-alvo.

                1. MICROFILTROS ARQUETÍPICOS

                Para cada perfil analisado, responda e registre, de forma objetiva, os seguintes pontos:

                a) Luz ou Sombra do Arquétipo

                Verifique e indique se o perfil manifesta predominância da luz (aspectos positivos, virtuosos, conscientes) ou da sombra (aspectos inconscientes, reprimidos ou distorcidos) do arquétipo.

                b) Linguagem Textual – Emocional ou Racional

                Analise a comunicação textual (bio, legendas, posts) e determine se ela é orientada mais para o emocional (expressão dos sentimentos, sensibilidade, intimidade) ou para o racional (lógica, objetividade, clareza argumentativa).

                c) Estética Visual – Ativa ou Receptiva

                Examine os elementos visuais (imagens, cores, composições) e identifique se a estética se manifesta de forma ativa (dinâmica, vibrante, enérgica) ou receptiva (suave, contemplativa, serena).

                Instruções: Avalie cada item de forma independente, utilizando insights das obras de Jung, e registre suas observações com uma justificativa concisa apoiada em termos simbólicos e estéticos.

                2. ESQUEMA DE PONTUAÇÃO

                Abaixo, elabore um sistema de pontuação que permita quantificar a análise em três dimensões, atribuindo uma nota de 0 a 5 para cada critério:

                a) Força Arquetípica

                Definição: Grau em que o arquétipo é claro e facilmente identificável no perfil.

                Escala:

                0: Ausência de definição

                1-2: Sinais tênues ou ambíguos

                3: Moderada presença

                4-5: Forte e inequívoca manifestação

                b) Coerência (Imagem x Texto x Energia)

                Definição: Grau de alinhamento entre os elementos visuais, a comunicação textual e a energia simbólica percebida.

                Escala:

                0: Inconsistência total entre os elementos

                1-2: Pequenas sinergias, mas com muitos contrastes

                3: Coerência moderada

                4-5: Alinhamento harmonioso e robusto de todos os elementos

                c) Alinhamento com o Público-Alvo

                Definição: Quão bem o perfil se comunica com o público-alvo desejado, considerando a ressonância dos valores e arquétipos apresentados.

                Escala:

                0: Desalinhamento evidente

                1-2: Alinhamento parcial e incerto

                3: Alinhamento razoável

                4-5: Excelente correspondência entre a comunicação do perfil e as expectativas do público

                Instruções: Para cada critério, justifique a pontuação com observações específicas baseadas nos dados visuais e textuais do perfil. Caso haja dúvidas ou ambiguidade em algum dos critérios, indique os pontos de atenção e possíveis áreas de ajuste.

                Exemplo de Instrução Final

                Ao final da análise, produza um relatório resumido que contenha:

                O resultado dos microfiltros (luz/sombra, emocional/racional, ativa/receptiva)

                A pontuação final para Força Arquetípica, Coerência e Alinhamento

                Uma síntese poética e estratégica que integre os dados e a pontuação, oferecendo um diagnóstico esclarecedor do posicionamento arquetípico do perfil.

                Mantenha a linguagem técnica e artística, fornecendo um feedback que permita ao usuário ajustar e potencializar sua comunicação com clareza e autenticidade.

                Aqui está uma lógica de análises:

                Comece com <Os Arquétipos e o Inconsciente Coletivo>.

                Em seguida, suba o <O Homem e Seus Símbolos>.

                Depois, adicione <Aion> e <Tipos Psicológicos>.
                """,
                "tools": [{
                    "type": "file_search",
                    "vector_store_ids": ["vs_67fe9e93b4208191a9171f2843142ac0"],
                    "max_num_results": 20
                }],
                "input": [
                    {
                        "role": "system",
                        "content": """
                        aqui estão os livros a sua disposição no vector de conhecimento:

                        1. <<Os Arquétipos e o Inconsciente Coletivo (The Archetypes and the Collective Unconscious)>>

                        Obra mais direta e central sobre arquétipos.

                        Define os principais arquétipos e discute o funcionamento do inconsciente coletivo.

                        Fala sobre o Self, a Sombra, a Persona, a Anima/Animus, entre outros.

                        Este é o livro número 9 da coleção "Obras Completas de Jung" (CW9/I).

                        2. <Aion: Estudos sobre o Simbolismo do Si-mesmo> (Aion: Researches into the Phenomenology of the Self)

                        Explora profundamente o arquétipo do Self e seu papel na individuação.

                        Analisa o símbolo de Cristo como representação do Self.

                        Muito útil para compreender dinâmicas de sombra, persona, anima/animus em níveis mais profundos.

                        Este é o volume 9/II das Obras Completas (CW9/II).

                        3. <Tipos Psicológicos> (Psychological Types)

                        Introduz os conceitos de introversão/extroversão e das funções cognitivas (sensação, intuição, pensamento, sentimento).

                        Essencial para treinar a IA a compreender o estilo de comunicação e expressão dos perfis (relacional vs lógico, objetivo vs subjetivo).

                        Volume 6 das Obras Completas (CW6).

                        4. <O Homem e Seus Símbolos> (Man and His Symbols)

                        Último livro de Jung, escrito para o público leigo.

                        Riquíssimo em simbologia imagética — excelente para treinar a IA na leitura simbólica de imagens, fotos e ícones.

                        Inclui ensaios de discípulos de Jung também.
                        """
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "aqui estão as imagens para a analise"},
                            {"type": "input_image", "image_url": bio_image_url},
                            {"type": "input_image", "image_url": profile_image_url},
                            {"type": "input_image", "image_url": feed_image_url}
                        ]
                    }
                ]
            }
            
            # Enviar a requisição POST
            response = requests.post(url, headers=headers, json=payload)
            
            # Verificar o status da resposta
            if response.status_code == 200:
                result = response.json()
                # Extrair o conteúdo da análise da resposta
                analysis_text = result.get('response', {}).get('content', '')
                if not analysis_text:
                    return False, "Resposta vazia da API"
                return True, analysis_text
            else:
                return False, f"Erro na requisição: {response.status_code} - {response.text}"
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f"Erro ao analisar imagens: {error_details}")
            return False, f"Erro ao analisar as imagens: {str(e)}"