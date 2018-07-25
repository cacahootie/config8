
DROP SCHEMA test_config8 CASCADE;

CREATE SCHEMA test_config8;

SET search_path TO test_config8;


CREATE TABLE documents (
    name text,
    document jsonb
);


create or replace function parse_reference(jref jsonb)
returns text language sql as $$
    SELECT CAST (
        (SELECT jref ->> '$ref')
        AS TEXT
    )
$$;

create or replace function reference_get_path(jref text)
returns text language sql as $$
    SELECT 
        case
            when position('#/' in jref) = 1 then null
            when position('#/' in jref) > 0 then substring(jref from 1 for position('#/' in jref) - 1)
            else jref
        end
$$;

create or replace function reference_get_ref(jref text)
returns text language sql as $$
    SELECT
        case
            when position('#/' in jref) > 0 
                then substring(jref from position('#/' in jref))
            else null
        end
$$;

create or replace function jref_to_jpath(jref text)
returns text[] language sql as $$
    SELECT (regexp_split_to_array(jref, '/'))[2:];
$$;

create or replace function jsonb_reference(jref text)
returns jsonb language sql as $$
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

/*
create or replace function jsonb_reference(jpath text, jref text[])
returns jsonb language sql as $$
    SELECT
        CASE
            WHEN reference_get_ref(jref) NOTNULL
                AND reference_get_path(jref) NOTNULL
                THEN (
                    SELECT document -> reference_get_ref(jref) FROM documents
                    WHERE name=reference_get_path(jref)
                )
            ELSE (
                SELECT document FROM documents 
                WHERE name=reference_get_path(jref)
            )
        END
$$;*/

create or replace function jsonb_reference(jref jsonb)
returns jsonb language sql as $$
    SELECT document FROM documents WHERE name=(
        parse_reference(jref)
    )
$$;

create or replace function jsonb_compile(target jsonb)
returns jsonb language sql as $$
    select jsonb_object_agg(
            key,
            case
                when jsonb_typeof(val) <> 'object' then val
                when val ? '$ref' then (jsonb_reference(val))
                else val
            end
        )
    from jsonb_each(target) e1(key, val)
$$;

create or replace function jsonb_merge_recurse(orig jsonb, delta jsonb)
returns jsonb language sql as $$
    select
        jsonb_object_agg(
            coalesce(keyOrig, keyDelta),
            case
                when valOrig isnull then valDelta
                when valDelta isnull then valOrig
                when (jsonb_typeof(valOrig) = 'array') then valOrig || valDelta
                when (jsonb_typeof(valOrig) <> 'object' or jsonb_typeof(valDelta) <> 'object') then valDelta
                else jsonb_merge_recurse(valOrig, valDelta)
            end
        )
    from jsonb_each(orig) e1(keyOrig, valOrig)
    full join jsonb_each(delta) e2(keyDelta, valDelta) on keyOrig = keyDelta
$$;

