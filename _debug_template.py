from flask import Flask
from flask import request
import json
app = Flask(__name__)

#-BEGIN CUSTOM HANDLERS
#-END CUSTOM HANDLERS

@app.route('/set_input_direct/<method>', methods=['POST'])
def set_input(method):
    func = method
    jdata = json.loads(request.data.decode("utf-8"))
    f = globals()[func]
    hashMap.d=jdata['hashmap']
    f()
    jdata['hashmap'] = hashMap.export()
    jdata['stop'] =False
    jdata['ErrorMessage']=""
    jdata['Rows']=[]

    return json.dumps(jdata)

@app.route('/post_screenshot', methods=['POST'])
def post_screenshot():
    d = request.data
    return "1"

class hashMap:
    d = {}
    def put(key,val):
        hashMap.d[key]=val
    def get(key):
        return hashMap.d.get(key)
    def remove(key):
        if key in hashMap.d:
            hashMap.d.pop(key)
    def containsKey(key):
        return  key in hashMap.d
    def export():
        ex_hashMap = []
        for key in hashMap.d.keys():
            ex_hashMap.append({"key":key,"value":hashMap.d[key]})
        return ex_hashMap

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=2075,debug=True)