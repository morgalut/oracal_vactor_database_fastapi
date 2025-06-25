-- Connect to PDB
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Info log
PROMPT === Creating user app_user in FREEPDB1 ===

-- Create user safely
BEGIN
  EXECUTE IMMEDIATE 'CREATE USER app_user IDENTIFIED BY "AppPassword123"';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -01920 THEN -- user already exists
      RAISE;
    END IF;
END;
/

-- Grant permissions
BEGIN
  EXECUTE IMMEDIATE 'GRANT CONNECT, RESOURCE TO app_user';
  EXECUTE IMMEDIATE 'ALTER USER app_user DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS';
EXCEPTION
  WHEN OTHERS THEN
    NULL; -- Permissions may already exist
END;
/

-- Use app_user schema
ALTER SESSION SET CURRENT_SCHEMA = app_user;

PROMPT === Creating documents_vectors table ===

-- Drop table if exists
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE documents_vectors';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN -- -942 = table or view does not exist
      RAISE;
    END IF;
END;
/

-- Create table with fallback BLOB vector type
BEGIN
  EXECUTE IMMEDIATE '
    CREATE TABLE documents_vectors (
      id VARCHAR2(100) PRIMARY KEY,
      text CLOB NOT NULL,
      vector BLOB,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  ';
EXCEPTION
  WHEN OTHERS THEN
    RAISE;
END;
/

PROMPT ✅ Table and user setup complete.
