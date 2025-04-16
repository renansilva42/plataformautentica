import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseManager:
    @staticmethod
    def sign_up(email, password, nome, telefone, instagram):
        """Register a new user in Supabase Auth and store additional data in profiles table"""
        try:
            # Create auth user
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Get the user's UUID
            user_id = auth_response.user.id
            
            # Check if email is confirmed
            # (Will typically be False if Supabase is configured for email confirmation)
            email_confirmed = auth_response.user.email_confirmed_at is not None
            
            # Store additional profile data
            profile_data = {
                "id": user_id,
                "nome": nome,
                "telefone": telefone,
                "instagram": instagram
            }
            
            # Insert profile data into the profiles table
            supabase.table("profiles").insert(profile_data).execute()
            
            # Return user_id and email confirmation status
            return True, user_id, email_confirmed
        except Exception as e:
            error_message = str(e)
            # Detailed log for debugging
            print(f"Erro no cadastro: {error_message}")
            return False, error_message, None
    
    @staticmethod
    def sign_in(email, password):
        """Sign in a user with Supabase Auth"""
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            return True, response
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_user_profile(user_id):
        """Get user profile data from profiles table"""
        try:
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if len(response.data) > 0:
                return True, response.data[0]
            return False, "Profile not found"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def update_user_profile(user_id, profile_data):
        """Update user profile data"""
        try:
            response = supabase.table("profiles").update(profile_data).eq("id", user_id).execute()
            return True, response.data
        except Exception as e:
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
            # Confirm email using the token
            response = supabase.auth.verify_otp({
                "token_hash": token,
                "type": "email_confirmation"
            })
            
            return True, "Email confirmado com sucesso"
        except Exception as e:
            error_message = str(e)
            print(f"Erro na confirmação de email: {error_message}")
            return False, error_message
