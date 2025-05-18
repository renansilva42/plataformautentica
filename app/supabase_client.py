import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"DEBUG: SUPABASE_URL='{SUPABASE_URL}'")  # Debug print to check value and whitespace

# Initialize Supabase client
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.debug("Supabase client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
    supabase = None

class SupabaseManager:
    @staticmethod
    def sign_up(email, password, nome, telefone, instagram):
        """Register a new user in Supabase Auth and store additional data in profiles table"""
        try:
            if supabase is None:
                logger.error("Supabase client is not initialized.")
                return False, "Supabase client not initialized", None

            logger.debug(f"Attempting to sign up user with email: {email}")
            # Check if user with this email already exists and access_expiration is still valid
            response = supabase.table("profiles").select("id, access_expiration").eq("email", email).execute()
            logger.debug(f"Profiles query response: {response}")
            if response.data and len(response.data) > 0:
                profile = response.data[0]
                access_expiration = profile.get("access_expiration")
                if access_expiration:
                    expiration_dt = datetime.fromisoformat(access_expiration)
                    if expiration_dt > datetime.now(ZoneInfo("America/Belem")):
                        logger.debug("User already registered with valid access expiration.")
                        return False, "Usuário já cadastrado e com acesso válido. Por favor, aguarde o término do período de acesso antes de tentar novamente.", None

            # Create auth user
            auth_response = supabase.auth.sign_up({
                "email": email.strip(),
                "password": password.strip()
            })
            logger.debug(f"Auth sign_up response: {auth_response}")

            # Get the user's UUID
            user_id = auth_response.user.id

            # Check if email is confirmed
            # (Will typically be False if Supabase is configured for email confirmation)
            email_confirmed = auth_response.user.email_confirmed_at is not None

            # Calculate access expiration timestamp (48 hours from now) in America/Belem timezone
            access_expiration = (datetime.now(ZoneInfo("America/Belem")) + timedelta(hours=48)).isoformat()

            # Store additional profile data including access_expiration
            profile_data = {
                "id": user_id,
                "email": email.strip(),
                "nome": nome.strip() if nome else None,
                "telefone": telefone.strip() if telefone else None,
                "instagram": instagram.strip() if instagram else None,
                "access_expiration": access_expiration
            }

            # Insert profile data into the profiles table
            insert_response = supabase.table("profiles").insert(profile_data).execute()
            logger.debug(f"Insert profile response: {insert_response}")

            # Return user_id and email confirmation status
            return True, user_id, email_confirmed
        except Exception as e:
            error_message = str(e)
            # Detailed log for debugging
            logger.error(f"Erro no cadastro: {error_message}", exc_info=True)
            return False, error_message, None
    
    @staticmethod
    def sign_in(email, password):
        """Sign in a user with Supabase Auth"""
        try:
            logger.debug(f"Attempting to sign in user with email: {email}")
            response = supabase.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            logger.debug(f"Sign in response: {response}")
            return True, response
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}", exc_info=True)
            return False, str(e)
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile data from profiles table"""
        try:
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            logger.debug(f"Get user profile response: {response}")
            if len(response.data) > 0:
                return True, response.data[0]
            return False, "Profile not found"
        except Exception as e:
            logger.error(f"Get user profile error: {str(e)}", exc_info=True)
            return False, str(e)
    
    @staticmethod
    def update_user_profile(user_id, profile_data):
        """Update user profile data"""
        try:
            response = supabase.table("profiles").update(profile_data).eq("id", user_id).execute()
            logger.debug(f"Update user profile response: {response}")
            return True, response.data
        except Exception as e:
            logger.error(f"Update user profile error: {str(e)}", exc_info=True)
            return False, str(e)
    
    @staticmethod
    def confirm_email(token):
        """
        Confirm user email with token from Supabase
        
        Args:
            token (str): Confirmation token from email link
            
        Returns:
            tuple: (success, result)
        """
        try:
            logger.debug(f"Attempting to confirm email with token: {token}")
            # Confirm email using the token
            response = supabase.auth.verify_otp({
                "token_hash": token,
                "type": "email_confirmation"
            })
            logger.debug(f"Email confirmation response: {response}")
            return True, "Email confirmado com sucesso"
        except Exception as e:
            error_message = str(e)
            logger.error(f"Erro na confirmação de email: {error_message}", exc_info=True)
            return False, error_message

    @staticmethod
    def insert_message_analista(user_id, thread_id, role, content, nome, instagram, telefone):
        """Insert a chat message into the messages_analista table"""
        try:
            message_data = {
                "user_id": user_id,
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "nome": nome,
                "instagram": instagram,
                "telefone": telefone
            }
            response = supabase.table("messages_analista").insert(message_data).execute()
            if response.status_code == 201 or response.status_code == 200:
                return True, response.data
            else:
                return False, response.data
        except Exception as e:
            logger.error(f"Insert message analista error: {str(e)}", exc_info=True)
            return False, str(e)

    @staticmethod
    def get_messages_by_thread_analista(thread_id):
        """Retrieve all messages for a given thread ordered by creation time from messages_analista"""
        try:
            response = supabase.table("messages_analista").select("*").eq("thread_id", thread_id).order("created_at", ascending=True).execute()
            if response.status_code == 200:
                return True, response.data
            else:
                return False, response.data
        except Exception as e:
            logger.error(f"Get messages by thread analista error: {str(e)}", exc_info=True)
            return False, str(e)

    @staticmethod
    def insert_message_conteudo(user_id, thread_id, role, content, nome, instagram, telefone):
        """Insert a chat message into the messages_conteudo table"""
        try:
            message_data = {
                "user_id": user_id,
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "nome": nome,
                "instagram": instagram,
                "telefone": telefone
            }
            response = supabase.table("messages_conteudo").insert(message_data).execute()
            if response.status_code == 201 or response.status_code == 200:
                return True, response.data
            else:
                return False, response.data
        except Exception as e:
            logger.error(f"Insert message conteudo error: {str(e)}", exc_info=True)
            return False, str(e)

    @staticmethod
    def insert_message_will_ai(user_id, thread_id, role, content, nome, instagram, telefone):
        """Insert a chat message into the messages_will_ai table"""
        try:
            message_data = {
                "user_id": user_id,
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "nome": nome,
                "instagram": instagram,
                "telefone": telefone
            }
            response = supabase.table("messages_will_ai").insert(message_data).execute()
            if response.status_code == 201 or response.status_code == 200:
                return True, response.data
            else:
                return False, response.data
        except Exception as e:
            logger.error(f"Insert message will_ai error: {str(e)}", exc_info=True)
            return False, str(e)

    @staticmethod
    def get_messages_by_thread_conteudo(thread_id):
        """Retrieve all messages for a given thread ordered by creation time from messages_conteudo"""
        try:
            response = supabase.table("messages_conteudo").select("*").eq("thread_id", thread_id).order("created_at", ascending=True).execute()
            if response.status_code == 200:
                return True, response.data
            else:
                return False, response.data
        except Exception as e:
            logger.error(f"Get messages by thread conteudo error: {str(e)}", exc_info=True)
            return False, str(e)
