
import json

def merge(base, overlay):
    if isinstance(base, str):
        base = json.loads(base)
    if isinstance(overlay, str):
        overlay = json.loads(overlay)
    
    for k, v in overlay.items():
        if (k in base and isinstance(base[k], list)) and isinstance(overlay[k], list):
            base[k] = base[k] + overlay[k]
            print(base[k])
        elif (k in base and isinstance(base[k], dict)) and isinstance(overlay[k], dict):
            merge(base[k], overlay[k])
        else:
            base[k] = overlay[k]
    return base