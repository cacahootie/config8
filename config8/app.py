
from base64 import urlsafe_b64decode

from flask import Flask, jsonify, request

from config8.merger import comp_web, comp, resolve

app = Flask('config8')

@app.route('/<path:path>')
def get_json(path):
    result = comp_web(path, request.args.get('jref'))
    return jsonify(result)

@app.route('/jsonreference', methods=['POST'])
def get_jsonreference():
    q = request.get_data(as_text=True)
    if '#' in q:
        f,o = q.split('#',1)
        base = comp(f)
        return jsonify(resolve('#{}'.format(o), base))
    else:
        return jsonify(comp(q))
