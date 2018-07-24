
import pytest
import psycopg2
from psycopg2.extras import Json

from config8.merger import resolve

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
        cur.execute(INSERT,(fn, Json(resolve(fn))))
    yield cur
    conn.rollback()

def test_retrieve(cursor):
    cursor.execute("""SELECT document FROM documents WHERE name='t_obj'""")
    r = cursor.fetchone()[0]
    assert r['a']['b']['c'][1] == 2

def test_r2(cursor):
    cursor.execute(
        """SELECT document FROM documents WHERE name=%s""",
        (simple.format('base'),)
    )
    r = cursor.fetchone()[0]
    assert 'a' in r





