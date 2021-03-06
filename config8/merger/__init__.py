
from collections import namedtuple
import json

def _resolve_file(path):
    with open(path) as f:
        return json.load(f)

def path_obj(path, obj):
    if isinstance(path, str) and path.startswith('#/'):
        path = path[2:].split('/')
    elif isinstance(path, str):
        raise ValueError("JSON reference path must start with '#/'")

    if not isinstance(path, list):
        raise ValueError('Path is not a list')

    if len(path) == 1:
        path = path[0]
        if isinstance(obj, list):
            path = int(path)
        return obj[path]
    else:
        base = path.pop(0)
        return path_obj(path, obj[base])

def resolve_urlfriendly(path, obj):
    path = '#/{}'.format(path.replace('.','/'))
    return resolve(path, obj)

def resolve(path, obj=None):
    if isinstance(path, dict) and '$ref' in path:
        path = path['$ref']

    if path.startswith('#'):
        return path_obj(path, obj)
    elif '#' in path:
        fpath, objpath = path.split('#', 1)
        wholeobj = _resolve_file(fpath)
        return path_obj('#{}'.format(objpath), wholeobj)
    else:
        return _resolve_file(path)

def comp_web(target_path, jref=None):
    if '#' in target_path:
        target_path, jref = target_path.split('#')
        jref = '#{}'.format(jref)
        base = comp(target_path)
        return resolve(jref, base)
    result = comp(target_path)
    if jref is not None:
        return resolve_urlfriendly(jref, result)
    return result


def _comp_obj(target):
    parent = target.pop('@parent') if '@parent' in target else None
    if parent is not None:
        parent = resolve(parent)
        target = merge(parent, target, True)
    for k, v in target.items():
        if isinstance(v, dict):
            if '@parent' in v:
                target[k] = _comp_obj(v)
            elif '$ref' in v:
                target[k] = resolve(v['$ref'], target)
    return target


def comp(target_path):
    if isinstance(target_path, str):
        target = resolve(target_path)
    else:
        target = target_path
    return _comp_obj(target)

def merge(base, overlay, lockable=False):
    lock = []
    if lockable and '@lock_names' in base:
        lock = set(base.pop('@lock_names'))
    for k, v in overlay.items():
        if k in lock:
            continue
        elif (k in base and isinstance(base[k], list)) and isinstance(overlay[k], list):
            base[k] = base[k] + overlay[k]
        elif (k in base and isinstance(base[k], dict)) and isinstance(overlay[k], dict):
            merge(base[k], overlay[k], lockable)
        else:
            base[k] = overlay[k]
    return base
