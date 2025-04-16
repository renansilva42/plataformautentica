-- Habilitar RLS na tabela profiles (caso ainda não esteja habilitado)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Criar política que permite ao serviço de autenticação inserir novos perfis
CREATE POLICY "Permitir inserção de perfis durante o cadastro" 
ON public.profiles 
FOR INSERT 
WITH CHECK (auth.uid() = id);

-- Criar política que permite usuários visualizarem seu próprio perfil
CREATE POLICY "Usuários podem ver seu próprio perfil" 
ON public.profiles 
FOR SELECT 
USING (auth.uid() = id);

-- Criar política que permite usuários atualizarem seu próprio perfil
CREATE POLICY "Usuários podem atualizar seu próprio perfil" 
ON public.profiles 
FOR UPDATE 
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);