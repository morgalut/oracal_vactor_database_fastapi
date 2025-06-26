-- Connect to pluggable database
ALTER SESSION SET CONTAINER = FREEPDB1;

-- === Log user creation ===
PROMPT === Creating user app_user in FREEPDB1 ===

-- Create app_user if not exists
BEGIN
  EXECUTE IMMEDIATE 'CREATE USER app_user IDENTIFIED BY "AppPassword123"';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -01920 THEN -- user already exists
      RAISE;
    END IF;
END;
/

-- Grant roles and quotas
BEGIN
  EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO app_user';
  EXECUTE IMMEDIATE 'ALTER USER app_user DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS';
EXCEPTION
  WHEN OTHERS THEN
    NULL; -- skip if already granted
END;
/

-- Set schema to app_user
ALTER SESSION SET CURRENT_SCHEMA = app_user;

PROMPT === Dropping existing documents_vectors table if exists ===

-- Drop table if exists
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE documents_vectors';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN -- table does not exist
      RAISE;
    END IF;
END;
/

PROMPT === Creating documents_vectors table ===

-- ✅ Create a valid schema compatible with LangChain and Oracle
BEGIN
  EXECUTE IMMEDIATE '
    CREATE TABLE documents_vectors (
      id VARCHAR2(100) PRIMARY KEY,
      text CLOB NOT NULL,
      embedding CLOB, -- Use BLOB to store binary vector data
      metadata CLOB,  -- Optional: store metadata (as JSON string)
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  ';
EXCEPTION
  WHEN OTHERS THEN
    RAISE;
END;
/

PROMPT ✅ Table and user setup complete.
