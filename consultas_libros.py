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


@app.route('/libros/disponibles', methods=['GET'])
def listar_libros_disponibles():
    libros_disponibles = list(collection.find({"cantidad_en_stock": {"$gt": 0}}))
    return jsonify(libros_disponibles)

@app.route('/libros/por-categoria/<categoria>', methods=['GET'])
def encontrar_libros_por_categoria(categoria):
    libros_por_categoria = list(collection.find({"categoria.nombre": categoria}))
    return jsonify(libros_por_categoria)

@app.route('/libros/por-autor/<nombre_autor>', methods=['GET'])
def buscar_libros_por_autor(nombre_autor):
    libros_por_autor = list(collection.find({"autor.nombre": nombre_autor}))
    return jsonify(libros_por_autor)

@app.route('/libros/ordenados-por-calificacion', methods=['GET'])
def libros_ordenados_por_calificacion():
    libros_ordenados = list(collection.find().sort(["calificacion", pymongo.DESCENDING]))
    return jsonify(libros_ordenados)

@app.route('/libros/precio-inferior-a-20', methods=['GET'])
def encontrar_libros_precio_inferior_20():
    libros_precio_inferior_20 = list(collection.find({"precio": {"$lt": 20}}))
    return jsonify(libros_precio_inferior_20)

@app.route('/libros/buscar-por-palabra-clave/<palabra_clave>', methods=['GET'])
def buscar_libros_por_palabra_clave(palabra_clave):
    libros_con_palabra_clave = list(collection.find({
        "$or": [
            {"titulo": {"$regex": palabra_clave, "$options": "i"}},
            {"descripcion": {"$regex": palabra_clave, "$options": "i"}}
        ]
    }))
    return jsonify(libros_con_palabra_clave)

@app.route('/autores/top-10-caros', methods=['GET'])
def autores_mas_caros():
    pipeline = [
        {
            "$unwind": "$libros"
        },
        {
            "$group": {
                "_id": "$autor.nombre",
                "total_precio_libros": {"$sum": "$libros.precio"}
            }
        },
        {
            "$sort": {"total_precio_libros": -1}
        },
        {
            "$limit": 10
        }
    ]

    autores_caros = list(collection.aggregate(pipeline))
    return jsonify(autores_caros)

@app.route('/libros/cantidad-en-stock/<id>', methods=['GET'])
def obtener_cantidad_en_stock(id):
    libro = collection.find_one({"_id": ObjectId(id)})
    if libro:
        cantidad_en_stock = libro.get("cantidad_en_stock", 0)
        return jsonify({"cantidad_en_stock": cantidad_en_stock})
    else:
        return jsonify({"message": "Libro no encontrado"}), 404
    

@app.route('/libros/precio-promedio', methods=['GET'])
def calcular_precio_promedio():
    pipeline = [
        {
            "$group": {
                "_id": None,
                "precio_promedio": {"$avg": "$precio"}
            }
        }
    ]

    resultado = list(collection.aggregate(pipeline))
    if resultado:
        precio_promedio = resultado[0]["precio_promedio"]
        return jsonify({"precio_promedio": precio_promedio})
    else:
        return jsonify({"message": "No se encontraron libros para calcular el precio promedio"}), 404

@app.route('/categorias', methods=['GET'])
def obtener_todas_las_categorias():
    pipeline = [
        {
            "$group": {
                "_id": "$categoria.id",
                "nombre": {"$first": "$categoria.nombre"}
            }
        }
    ]

    categorias = list(collection.aggregate(pipeline))
    return jsonify(categorias)