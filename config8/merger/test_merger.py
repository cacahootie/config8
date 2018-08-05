
from pprintpp import pprint

import pytest

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

def test_compile_references():
    result = comp(simple.format('overlay'))
    pprint(result)
    assert result['e'] == 'the first letter'
    assert result['copy-a'] == 'this is an override'

def test_compile_parent():
    result = comp(simple.format('overlay'))
    pprint(result)
    assert "@parent" not in result
    _validate_overlay(result)

def test_compile_parent_nested():
    result = comp(simple.format('overlay'))
    pprint(result)
    assert "@parent" not in result['names']
    assert result['names']['bob'] == 'old'
    assert result['names']['jimmy'] == 'farnsworth'

def test_compile_lock_names():
    """Merge function respects @lock_names."""
    result = comp(simple.format('overlay'))
    pprint(result)
    assert '@lock_names' not in result
    assert result['immortal'] == 'lives forever'

def test_compile_lock_names_nested():
    """Merge function respects nested @lock_names."""
    result = comp(simple.format('overlay'))
    pprint(result)
    assert '@lock_names' not in result['d']
    assert result['d']['2'] == 'two'

base = resolve(simple.format('base'))
overlay = resolve(simple.format('overlay'))
merge_result = merge(base, overlay)

def test_merger():
    """Merge function can deep merge two dicts."""
    _validate_overlay(merge_result)
    assert "@parent" in merge_result
    assert '$ref' in merge_result['e']
    assert '$ref' in merge_result['copy-a']
    assert merge_result['immortal'] == 'I have risen'

def _validate_overlay(result):
    """Verify the merged output of the base and overlay."""
    assert result['a'] == 'this is an override'
    assert result['d']["3"] == 'three'
    assert len(result['b']) == 4
    assert result['b'][3] == 'item4'
    
