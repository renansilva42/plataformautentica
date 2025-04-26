-- Migration to add access_expiration column to profiles table
ALTER TABLE public.profiles
ADD COLUMN access_expiration TIMESTAMP;
