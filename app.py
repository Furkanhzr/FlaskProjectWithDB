from flask import Flask, jsonify, request, redirect
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields, ValidationError
import pymysql

app = Flask(__name__)
CORS(app)
api = Api(app)

# Veritabanı bağlantısı
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",  # Şifrenizi buraya ekleyin
        database="flask_test",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Marshmallow schema for validation
class ItemSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)

item_schema = ItemSchema()

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_DOCS_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_DOCS_URL,
    config={'app_name': "Flask CRUD API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/')
def home():
    """Root endpoint; redirects to Swagger UI."""
    return redirect("/swagger")


class Item(Resource):
    def get(self, item_id=None):
        """
        Get all items or a single item by ID.
        """
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if item_id:
                sql = "SELECT * FROM item WHERE id=%s"
                cursor.execute(sql, (item_id,))
                result = cursor.fetchone()
                if not result:
                    return {"message": "Item not found"}, 404
                return {"item": result}, 200
            else:
                sql = "SELECT * FROM item"
                cursor.execute(sql)
                results = cursor.fetchall()
                return {"items": results}, 200

    def post(self):
        """
        Create a new item.
        """
        try:
            data = item_schema.load(request.get_json())
        except ValidationError as err:
            return {"message": "Invalid input", "errors": err.messages}, 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO item (name, price) VALUES (%s, %s)"
            cursor.execute(sql, (data["name"], data["price"]))
            conn.commit()
            new_id = cursor.lastrowid
            data["id"] = new_id

        return {"message": "Item created", "item": data}, 201

    def put(self, item_id):
        """
        Update an existing item by ID.
        """
        try:
            data = item_schema.load(request.get_json())
        except ValidationError as err:
            return {"message": "Invalid input", "errors": err.messages}, 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Önce item var mı diye kontrol et
            check_sql = "SELECT * FROM item WHERE id=%s"
            cursor.execute(check_sql, (item_id,))
            existing_item = cursor.fetchone()
            if not existing_item:
                return {"message": "Item not found"}, 404

            # Güncelle
            update_sql = "UPDATE item SET name=%s, price=%s WHERE id=%s"
            cursor.execute(update_sql, (data["name"], data["price"], item_id))
            conn.commit()

            # Güncellenmiş hali al
            cursor.execute(check_sql, (item_id,))
            updated_item = cursor.fetchone()

        return {"message": "Item updated", "item": updated_item}, 200

    def delete(self, item_id):
        """
        Delete an item by ID.
        """
        conn = get_db_connection()
        with conn.cursor() as cursor:
            check_sql = "SELECT * FROM item WHERE id=%s"
            cursor.execute(check_sql, (item_id,))
            existing_item = cursor.fetchone()
            if not existing_item:
                return {"message": "Item not found"}, 404

            delete_sql = "DELETE FROM item WHERE id=%s"
            cursor.execute(delete_sql, (item_id,))
            conn.commit()

        return {"message": "Item deleted"}, 200


# API Endpoints
api.add_resource(Item, '/items', '/items/<string:item_id>')


@app.route('/static/swagger.json')
def swagger_json():
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "Flask CRUD API",
            "description": "A sample API for CRUD operations with MySQL",
            "version": "1.0.0"
        },
        "host": "localhost:5000",
        "basePath": "/",
        "schemes": ["http"],
        "tags": [
            {
                "name": "Items",
                "description": "Item management operations"
            }
        ],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {
            "/items": {
                "get": {
                    "tags": ["Items"],
                    "summary": "Get all items",
                    "responses": {
                        "200": {
                            "description": "A list of items"
                        }
                    }
                },
                "post": {
                    "tags": ["Items"],
                    "summary": "Create a new item",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "price": {"type": "number"}
                                },
                                "required": ["name", "price"]
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Item created"
                        },
                        "400": {
                            "description": "Invalid input"
                        }
                    }
                }
            },
            "/items/{item_id}": {
                "get": {
                    "tags": ["Items"],
                    "summary": "Get a specific item",
                    "parameters": [
                        {
                            "name": "item_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Item details"
                        },
                        "404": {
                            "description": "Item not found"
                        }
                    }
                },
                "put": {
                    "tags": ["Items"],
                    "summary": "Update an item",
                    "parameters": [
                        {
                            "name": "item_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        },
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "price": {"type": "number"}
                                },
                                "required": ["name", "price"]
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Item updated"
                        },
                        "400": {
                            "description": "Invalid input"
                        },
                        "404": {
                            "description": "Item not found"
                        }
                    }
                },
                "delete": {
                    "tags": ["Items"],
                    "summary": "Delete an item",
                    "parameters": [
                        {
                            "name": "item_id",
                            "in": "path",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Item deleted"
                        },
                        "404": {
                            "description": "Item not found"
                        }
                    }
                }
            }
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
