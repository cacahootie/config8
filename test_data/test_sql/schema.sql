
DROP SCHEMA test_config8 CASCADE;

CREATE SCHEMA test_config8;

SET search_path TO test_config8;

CREATE TABLE documents (
    name text,
    document jsonb
);
