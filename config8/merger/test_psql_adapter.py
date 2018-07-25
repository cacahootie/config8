
from pprintpp import pprint

import pytest
import psycopg2
from psycopg2.extras import Json

from config8.merger import resolve as f_resolve
from config8.merger.psql_adapter import resolve, merge, comp

simple = 'test_data/simple/{}.json'

t_obj = {
    'a': {
        'b': {
            'c': [1,2,3]
        }
    }
}

INSERT = """INSERT INTO documents VALUES (%s, %s)"""

@pytest.fixture
def cursor():
    conn = psycopg2.connect('dbname=test_config8')
    cur = conn.cursor()
    cur.execute("""SET search_path to test_config8""")
    cur.execute(INSERT,('t_obj', Json(t_obj)))
    for x in ('base', 'subbase', 'overlay'):
        fn = simple.format(x)
        cur.execute(INSERT,(fn, Json(f_resolve(fn))))
    yield cur
    conn.rollback()

def test_retrieve(cursor):
    cursor.execute("""SELECT document FROM documents WHERE name='t_obj'""")
    r = cursor.fetchone()[0]
    assert r['a']['b']['c'][1] == 2

def test_reference_get_path(cursor):
    cursor.execute("""
        SELECT reference_get_path(%s)
    """, ('a/b/c.json#/i/j/k',))
    r = cursor.fetchone()[0]
    assert r == 'a/b/c.json'

def test_reference_get_path_noref(cursor):
    cursor.execute("""
        SELECT reference_get_path(%s)
    """, ('a/b/c.json',))
    r = cursor.fetchone()[0]
    assert r == 'a/b/c.json'

def test_reference_get_path_nopath(cursor):
    cursor.execute("""
        SELECT reference_get_path(%s)
    """, ('#/a/b/c',))
    r = cursor.fetchone()[0]
    assert r == None

def test_reference_get_ref(cursor):
    cursor.execute("""
        SELECT reference_get_ref(%s)
    """, ('a/b/c.json#/i/j/k',))
    r = cursor.fetchone()[0]
    assert r == '#/i/j/k'

def test_reference_get_ref_simple(cursor):
    cursor.execute("""
        SELECT reference_get_ref(%s)
    """, ('t_obj#/a',))
    r = cursor.fetchone()[0]
    assert r == '#/a'

def test_reference_get_ref_noref(cursor):
    cursor.execute("""
        SELECT reference_get_ref(%s)
    """, ('a/b/c.json',))
    r = cursor.fetchone()[0]
    assert r == None

def test_reference_get_ref_nopath(cursor):
    cursor.execute("""
        SELECT reference_get_ref(%s)
    """, ('a/b/c.json#/i/j/k',))
    r = cursor.fetchone()[0]
    assert r == '#/i/j/k'

def test_parse_reference(cursor):
    cursor.execute("""
        SELECT parse_reference(%s)
    """, (Json({'$ref':'a/b/c.json#/i/j/k'}),)
    )
    r = cursor.fetchone()[0]
    assert r == 'a/b/c.json#/i/j/k'

def test_r2(cursor):
    cursor.execute(
        """SELECT document FROM documents WHERE name=%s""",
        (simple.format('base'),)
    )
    r = cursor.fetchone()[0]
    assert 'a' in r

def test_jref_to_jpath_multi(cursor):
    cursor.execute(
        """SELECT jref_to_jpath(%s)""",
        ('#/a/b/c',)
    )
    r = cursor.fetchone()[0]
    assert r == ['a','b','c']

def test_jref_to_jpath_single(cursor):
    cursor.execute(
        """SELECT jref_to_jpath(%s)""",
        ('#/a',)
    )
    r = cursor.fetchone()[0]
    assert r == ['a']

def test_jref_to_jpath_reference_get_ref(cursor):
    cursor.execute(
        """SELECT jref_to_jpath(reference_get_ref(%s))""",
        ('t_obj#/a',)
    )
    r = cursor.fetchone()[0]
    assert r == ['a']

def test_resolve_document(cursor):
    """Can resolve a document name."""
    r = resolve(cursor, simple.format('overlay'))
    assert isinstance(r, dict)
    assert '@parent' in r
    assert 'e' in r

def test_resolve_obj(cursor):
    """Can resolve a single-level path in an object."""
    r = resolve(cursor, 't_obj#/a')
    pprint(r)
    assert isinstance(r, dict)
    assert 'b' in r

def test_resolve_obj_multi(cursor):
    """Can resolve a single-level path in an object."""
    r = resolve(cursor, 't_obj#/a/b')
    pprint(r)
    assert isinstance(r, dict)
    assert 'c' in r

def test_merger(cursor):
    """Merge function can deep merge two dicts."""
    base = simple.format('base')
    overlay = simple.format('overlay')
    merge_result = merge(cursor, base, overlay)
    pprint(merge_result)
    _validate_merge(merge_result)
    assert "@parent" in merge_result

def test_compiler(cursor):
    overlay = simple.format('overlay')
    result = comp(cursor, overlay)
    pprint(result)
    _validate_merge(result)
    _validate_comp(result)
    assert "@parent" in result

def _validate_merge(result):
    """Verify the merged output of the base and overlay."""
    assert result['a'] == 'this is an override'
    assert result['d']["3"] == 'three'
    #assert len(result['b']) == 4
    #assert result['b'][3] == 'item4'

def _validate_comp(result):
    #assert result['e'] == 'the first letter'
    #assert result['copy-a'] == 'this is an override'
    pass
