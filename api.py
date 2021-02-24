from flask import Flask, jsonify, request
from pprint import pprint
from marshmallow import Schema, fields, ValidationError
import requests
import re
from bs4 import BeautifulSoup
import copy
import json


def consulta(diccionario):
  final_list = []
  etiquetas = ["", "soluciones", "componentes", "equipo", "blog"]
  words = ["identidad", "biometría"]
  for etiqueta in etiquetas:
    for word in words:
      req = requests.get("https://reconoserid.com/"+etiqueta, headers={"User-Agent": "XY"})
      soup = BeautifulSoup(req.text, 'html.parser')
      label = []
      for tag in soup.find_all(True):
          label.append(tag.name)

      label = set(label)

      dic = {}

      for l in label:
        k = soup.findAll(l, text = re.compile(word))
        if len(k) != 0:
          dic[l] = len(k)

      diccionario[word] = dic
      aux = copy.deepcopy(diccionario)
    final_list.append(aux)

  return final_list

class BandMemberSchema(Schema):
    biometría = fields.Dict(required=True)
    identidad = fields.Dict(required=True)


app = Flask(__name__)

@app.route("/", methods=['POST'])
def contar():
    values = json.loads(request.data)
    req = requests.get(values['url'], headers={"User-Agent": "XY"})
    soup = BeautifulSoup(req.text, 'html.parser')
    dic = {}
    dic[values['label']] = len(soup.find_all(values['label']))

    print(dic)
    return jsonify(dic)

@app.route("/", methods=['GET'])
def informe():
    diccionario = {}
    user_data = consulta(diccionario)
    try:
        BandMemberSchema(many=True).load(user_data)
        print('formato correcto')
    except ValidationError as err:
        pprint(err.messages)
    return jsonify(user_data)

if __name__ == "__main__":
    app.run(debug=True)




