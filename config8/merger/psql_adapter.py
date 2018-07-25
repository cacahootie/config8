
import psycopg2
from psycopg2.extras import Json

SELECT_REFERENCE = """
    SELECT jsonb_reference(%s)
"""

SELECT_DOCUMENT = """
    SELECT document FROM documents WHERE name=%s
"""

SELECT_MERGE = """
    SELECT jsonb_merge_recurse(
        ({}), ({})
    )
""".format(SELECT_DOCUMENT, SELECT_DOCUMENT)

SELECT_COMPILE = """
    SELECT jsonb_compile(({}))
""".format(SELECT_REFERENCE)


def resolve(cursor, path, obj=None):
    cursor.execute(SELECT_REFERENCE, (path,))
    return cursor.fetchone()[0]

def merge(cursor, base, overlay):
    cursor.execute(SELECT_MERGE, (base, overlay))
    return cursor.fetchone()[0]

def comp(cursor, target):
    cursor.execute(SELECT_COMPILE, (target,))
    return cursor.fetchone()[0]
