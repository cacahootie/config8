
from pprint import pprint

from config8.merger import merge, resolve, comp, path_obj

simple = 'test_data/simple/{}.json'

t_obj = {
    'a': {
        'b': {
            'c': [1,2,3]
        }
    }
}

def test_resolve_file():
    """Can resolve a filename."""
    r = resolve(simple.format('overlay'))
    assert isinstance(r, dict)
    assert '@parent' in r
    assert 'e' in r

def test_resolve_obj():
    """Can resolve a single-level path in an object."""
    r = resolve('#/a', t_obj)
    assert isinstance(r, dict)
    assert 'b' in r

def test_resolve_obj_nested_dict():
    """Can resolve a nested jsonreference."""
    r = resolve('#/a/b/c', t_obj)
    assert r == [1,2,3]

def test_resolve_obj_nested_list():
    """Resolver can resolve a nested jsonreference with an array/list."""
    r = resolve('#/a/b/c/1', t_obj)
    assert r == 2

def test_path_obj():
    """Path evaluator can resolve a nested jsonreference with an array/list."""
    r = path_obj('#/a/b/c/1', t_obj)
    assert r == 2

def test_compile():
    """Compiler can compile a file from a filename."""
    result = comp(simple.format('overlay'))
    pprint(result)
    _validate_overlay(result)
    assert "@parent" not in result
    assert result['names']['bob'] == 'old'
    assert result['names']['jimmy'] == 'farnsworth'

base = resolve(simple.format('base'))
overlay = resolve(simple.format('overlay'))
merge_result = merge(base, overlay)

def test_merger():
    """Merge function can deep merge two dicts."""
    _validate_overlay(merge_result)
    assert "@parent" in merge_result

def test_merger_lock_names():
    """Merge function respects @lock_names."""
    assert merge_result['immortal'] == 'lives forever'

def test_merger_lock_names_nested():
    """Merge function respects nested @lock_names."""
    assert merge_result['d']['2'] == 'two'

def _validate_overlay(result):
    """Verify the merged output of the base and overlay."""
    assert result['a'] == 'this is an override'
    assert result['d']["3"] == 'three'
    assert len(result['b']) == 4
    assert result['b'][3] == 'item4'
    assert result['e'] == 'the first letter'
    assert result['copy-a'] == 'this is an override'
