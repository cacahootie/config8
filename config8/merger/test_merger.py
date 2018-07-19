
from config8.merger import merge

simple = 'test_data/simple/{}.json'

def test_merger():
    with open(simple.format('base')) as base, \
            open(simple.format('overlay')) as overlay:
        base_str = base.read()
        overlay_str = overlay.read()
        result = merge(base_str, overlay_str)
        assert result['a'] == 'this is an override'
        assert result['d']["2"] == '2'
        assert result['d']["3"] == 'three'
        assert len(result['b']) == 4
        assert result['b'][3] == 'item4'
