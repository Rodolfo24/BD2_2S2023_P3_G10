from flask import Flask, request, jsonify
from bson import ObjectId
from bson.json_util import dumps
import pymongo

app = Flask(__name__)

# Conecta a la base de datos de MongoDB
client = pymongo.MongoClient('mongodb://user:1234@ac-idgyi4w-shard-00-00.ciwruv5.mongodb.net:27017,ac-idgyi4w-shard-00-01.ciwruv5.mongodb.net:27017,ac-idgyi4w-shard-00-02.ciwruv5.mongodb.net:27017/?replicaSet=atlas-u9kl0f-shard-0&ssl=true&authSource=admin')
db = client['practica3']
collection = db['Libros']  # Colección única para libros
collection.create_index([("titulo", "text"), ("descripcion", "text")])
# Endpoints para las operaciones CRUD

@app.route('/libros', methods=['GET'])
def leer_libros():
    busqueda = request.args.get('q')
    if busqueda:
        libros = list(collection.find({"$text": {"$search": busqueda}}))
    else:
        libros = list(collection.find())

    # Convertir ObjectId a strings para que sean serializables como JSON
    for libro in libros:
        libro['_id'] = str(libro['_id'])

    return dumps(libros)

@app.route('/libros', methods=['POST'])
def crear_libro():
    nuevo_libro = request.json

    # Verifica si el autor ya existe, si no, agregalo al libro
    autor = nuevo_libro.get("autor")
    autor_obj = autor or {}
    autor_id = None

    if "nombre" in autor:
        autor_obj["nombre"] = autor["nombre"]

    if "fecha_nacimiento" in autor:
        autor_obj["fecha_nacimiento"] = autor["fecha_nacimiento"]

    if autor_obj:
        autor_id = autor_id or ObjectId()
        autor_obj["_id"] = autor_id

    nuevo_libro["autor"] = autor_obj

    # Verifica si la categoría ya existe, si no, agregala al libro
    categoria = nuevo_libro.get("categoria")
    categoria_obj = categoria or {}
    categoria_id = None

    if "nombre" in categoria:
        categoria_obj["nombre"] = categoria["nombre"]

    if categoria_obj:
        categoria_id = categoria_id or ObjectId()
        categoria_obj["_id"] = categoria_id

    nuevo_libro["categoria"] = categoria_obj

    # Crea el libro con los datos actualizados
    libro_id = collection.insert_one(nuevo_libro).inserted_id
    return jsonify({"message": "Libro creado exitosamente", "libro_id": str(libro_id)})

@app.route('/libros/<id>', methods=['PUT'])
def actualizar_libro(id):
    nuevos_datos = request.json
    collection.update_one({"_id": ObjectId(id)}, {"$set": nuevos_datos})
    return jsonify({"message": "Libro actualizado exitosamente"})

@app.route('/libros/<id>', methods=['DELETE'])
def borrar_libro(id):
    collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Libro borrado exitosamente"})

if __name__ == '__main__':
    app.run(debug=True)
