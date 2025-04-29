import os
import requests
import json
import time
import base64
from flask import current_app

class OpenAIManager:
    """Classe para gerenciar chamadas à API do OpenAI"""
    
    @staticmethod
    def verify_assistant(assistant_id, headers):
        """
        Verifica se o assistant existe e está acessível
        
        Args:
            assistant_id (str): ID do assistant a ser verificado
            headers (dict): Headers para a requisição
            
        Returns:
            bool: True se o assistant existe, False caso contrário
        """
        try:
            base_url = "https://api.openai.com/v1"
            get_assistant_url = f"{base_url}/assistants/{assistant_id}"
            
            response = requests.get(get_assistant_url, headers=headers, timeout=30)
            return response.status_code == 200
        except:
            return False
            
    @staticmethod
    def capivara_analista_chat(message, message_type, user_profile):
        """
        Envia uma mensagem para o assistente Capivara Analista usando a API OpenAI Assistants API

        Args:
            message (str): Mensagem do usuário (texto ou URL para imagem)
            message_type (str): 'text', 'image', or 'image_file'
            user_profile (dict): Perfil do usuário (pode ser usado para contexto)

        Returns:
            str: Resposta do assistente
        """
        import requests
        import time
        from flask import current_app
        try:
            api_key = current_app.config.get('OPENAI_API_KEY_ANALISTA') or os.getenv('OPENAI_API_KEY_ANALISTA')
            assistant_id = os.getenv('OPENAI_CAPIVARA_ANALISTA_ASSISTANT_ID')

            if not api_key:
                raise Exception("API key não configurada")
            if not assistant_id:
                raise Exception("OPENAI_CAPIVARA_ANALISTA_ASSISTANT_ID não configurado na variável de ambiente")

            current_app.logger.info(f"Usando assistant ID: {assistant_id}")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "OpenAI-Beta": "assistants=v2"
            }

            base_url = "https://api.openai.com/v1"

            # Step 1: Create a thread
            create_thread_url = f"{base_url}/threads"
            thread_response = requests.post(create_thread_url, headers=headers, json={}, timeout=30)
            if thread_response.status_code not in (200, 201):
                raise Exception(f"Erro ao criar thread: {thread_response.status_code} - {thread_response.text}")
            thread_data = thread_response.json()
            thread_id = thread_data.get('id')
            if not thread_id:
                raise Exception("ID da thread não retornado")

            message_content = []

            # If message_type is image_file, upload the image first to get file_id
            if message_type == 'image_file':
                upload_url = f"{base_url}/files"
                upload_headers = {
                    "Authorization": f"Bearer {api_key}"
                }
                # Prepare multipart/form-data payload for file upload
                files = {
                    "file": ("image.png", base64.b64decode(message), "image/png"),
                    "purpose": (None, "vision")
                }
                upload_response = requests.post(upload_url, headers=upload_headers, files=files, timeout=60)
                if upload_response.status_code not in (200, 201):
                    raise Exception(f"Erro ao enviar arquivo: {upload_response.status_code} - {upload_response.text}")
                upload_data = upload_response.json()
                file_id = upload_data.get('id')
                if not file_id:
                    raise Exception("ID do arquivo não retornado no upload")

                # Prepare message content with file_id
                message_content.append({
                    "type": "image_file",
                    "image_file": {
                        "file_id": file_id,
                        "detail": "high"
                    }
                })
            elif message_type == 'text':
                message_content.append({
                    "type": "text",
                    "text": message
                })
            elif message_type == 'image':
                # Validate image URL format
                if not (isinstance(message, str) and (message.startswith("http://") or message.startswith("https://"))):
                    raise Exception("Formato de imagem inválido. Deve ser uma URL pública começando com http:// ou https://")

                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": message,
                        "detail": "high"
                    }
                })
            else:
                raise Exception("Tipo de mensagem inválido. Use 'text', 'image' ou 'image_file'.")

            # Step 2: Add message to the thread
            add_message_url = f"{base_url}/threads/{thread_id}/messages"

            message_payload = {
                "role": "user",
                "content": message_content
            }

            message_response = requests.post(add_message_url, headers=headers, json=message_payload, timeout=30)
            if message_response.status_code not in (200, 201):
                raise Exception(f"Erro ao adicionar mensagem: {message_response.status_code} - {message_response.text}")

            # Step 3: Create a run to get assistant response
            create_run_url = f"{base_url}/threads/{thread_id}/runs"
            run_payload = {
                "assistant_id": assistant_id,
            }
            current_app.logger.info(f"Criando run para thread {thread_id} com assistant {assistant_id}")
            run_response = requests.post(create_run_url, headers=headers, json=run_payload, timeout=60)
            if run_response.status_code not in (200, 201):
                raise Exception(f"Erro ao criar run: {run_response.status_code} - {run_response.text}")
            run_data = run_response.json()
            run_id = run_data.get('id')

            # Step 4: Wait for the run to complete
            max_retries = 60
            retries = 0
            while retries < max_retries:
                check_run_url = f"{base_url}/threads/{thread_id}/runs/{run_id}"
                run_status_response = requests.get(check_run_url, headers=headers, timeout=30)
                if run_status_response.status_code != 200:
                    raise Exception(f"Erro ao verificar status do run: {run_status_response.status_code} - {run_status_response.text}")

                run_status_data = run_status_response.json()
                status = run_status_data.get('status')

                if status == 'completed':
                    break
                elif status in ['failed', 'cancelled', 'expired']:
                    raise Exception(f"Run terminou com status: {status}")

                time.sleep(5)
                retries += 1

            if retries >= max_retries:
                raise Exception("Tempo limite excedido aguardando a resposta do assistente")

            # Step 5: Retrieve messages after run completion
            list_messages_url = f"{base_url}/threads/{thread_id}/messages"
            messages_response = requests.get(list_messages_url, headers=headers, timeout=30)
            if messages_response.status_code != 200:
                raise Exception(f"Erro ao listar mensagens: {messages_response.status_code} - {messages_response.text}")

            messages_data = messages_response.json()
            messages = messages_data.get('data', [])

            assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
            if not assistant_messages:
                raise Exception("Nenhuma resposta do assistente encontrada")

            latest_assistant_message = assistant_messages[0]

            content_parts = latest_assistant_message.get('content', [])
            assistant_response = ""

            for part in content_parts:
                if part.get('type') == 'text':
                    text_part = part.get('text', '')
                    if isinstance(text_part, str):
                        assistant_response += text_part
                    elif isinstance(text_part, dict):
                        assistant_response += part.get('value', str(text_part))
                    else:
                        assistant_response += str(text_part)

            if not assistant_response:
                raise Exception("Conteúdo da resposta do assistente vazio")

            return assistant_response

        except Exception as e:
            current_app.logger.error(f"Erro na comunicação com a API: {str(e)}")
            raise e
