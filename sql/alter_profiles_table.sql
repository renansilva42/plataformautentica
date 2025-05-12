-- SQL command to alter the profiles table to the correct schema

-- Add profile_photo_url column if it does not exist
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS profile_photo_url TEXT;

-- Ensure id column is UUID and primary key (adjust if needed)
ALTER TABLE profiles
ALTER COLUMN id SET DATA TYPE UUID USING id::uuid;

ALTER TABLE profiles
DROP CONSTRAINT IF EXISTS profiles_pkey CASCADE;

ALTER TABLE profiles
ADD PRIMARY KEY (id);

-- Add other necessary columns with appropriate types if missing
-- Example: nome, telefone, instagram, access_expiration

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS nome TEXT;

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS telefone TEXT;

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS instagram TEXT;

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS access_expiration TIMESTAMP WITH TIME ZONE;

-- Add unique constraint on email if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_email'
    ) THEN
        ALTER TABLE profiles ADD CONSTRAINT unique_email UNIQUE (email);
    END IF;
END
$$;
