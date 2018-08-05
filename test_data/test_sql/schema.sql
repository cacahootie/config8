
DROP SCHEMA test_config8 CASCADE;

CREATE SCHEMA test_config8;

SET search_path TO test_config8;


CREATE TABLE documents (
    name text,
    document jsonb
);


CREATE OR REPLACE FUNCTION parse_reference(jref jsonb)
RETURNS text LANGUAGE sql AS $$
    SELECT CAST (
        (SELECT jref ->> '$ref')
        AS text
    )
$$;

CREATE OR REPLACE FUNCTION reference_get_path(jref text)
RETURNS text LANGUAGE sql AS $$
    SELECT 
        CASE
            WHEN position('#/' in jref) = 1
                then null
            WHEN position('#/' in jref) > 0
                then substring(jref from 1 for position('#/' in jref) - 1)
            ELSE jref
        END
$$;

CREATE OR REPLACE FUNCTION reference_get_ref(jref text)
RETURNS text LANGUAGE sql AS $$
    SELECT
        CASE
            WHEN position('#/' in jref) > 0
                THEN substring(jref from position('#/' in jref))
            ELSE NULL
        END
$$;

CREATE OR REPLACE FUNCTION jref_to_jpath(jref text)
RETURNS text[] LANGUAGE sql AS $$
    SELECT (regexp_split_to_array(jref, '/'))[2:];
$$;

CREATE OR REPLACE FUNCTION jsonb_reference(jref text)
RETURNS jsonb LANGUAGE sql as $$
    SELECT
        CASE
            WHEN reference_get_ref(jref) NOTNULL
                AND reference_get_path(jref) NOTNULL
                THEN (
                    SELECT document #>
                        jref_to_jpath(reference_get_ref(jref)) 
                    FROM documents
                    WHERE name=reference_get_path(jref)
                )
            ELSE (
                SELECT document FROM documents 
                WHERE name=reference_get_path(jref)
            )
        END
$$;

CREATE OR REPLACE FUNCTION jsonb_reference(jref jsonb)
RETURNS jsonb LANGUAGE sql as $$
    SELECT document FROM documents WHERE name=(
        parse_reference(jref)
    )
$$;

CREATE OR REPLACE FUNCTION jsonb_reference(jref jsonb, base jsonb)
RETURNS jsonb LANGUAGE sql as $$
    SELECT base #>
        jref_to_jpath(reference_get_ref(parse_reference(jref)))
$$;

CREATE OR REPLACE FUNCTION jsonb_compile(target jsonb)
RETURNS jsonb LANGUAGE sql as $$
    SELECT 

                jsonb_object_agg(
                    key,
                    CASE
                        WHEN jsonb_typeof(val) <> 'object'
                            THEN val
                        WHEN val ? '$ref'
                            THEN (jsonb_reference(val))
                        ELSE val
                    END
                )
    FROM jsonb_each(target) e1(key, val)
$$;

CREATE OR REPLACE FUNCTION jsonb_merge_recurse(base jsonb, overlay_ jsonb)
RETURNS jsonb LANGUAGE sql as $$
    SELECT
        jsonb_object_agg(
            coalesce(keyBase, keyOverlay),
            CASE
                WHEN valBase isnull
                    THEN valOverlay
                WHEN valOverlay isnull
                    THEN valBase
                WHEN (jsonb_typeof(valOverlay) <> 'object') AND (valOverlay ? '$ref')
                    THEN jsonb_reference(valOverlay, overlay_)
                WHEN (jsonb_typeof(valBase) = 'array')
                    THEN valBase || valOverlay
                WHEN (jsonb_typeof(valBase) <> 'object' OR jsonb_typeof(valOverlay) <> 'object')
                    THEN valOverlay
                ELSE jsonb_merge_recurse(valBase, valOverlay)
            END
        )
    FROM jsonb_each(base) e1(keyBase, valBase)
    FULL JOIN jsonb_each(overlay_) e2(keyOverlay, valOverlay)
        ON keyBase = keyOverlay
$$;

