import traceback
from pymongo import MongoClient

from flask import Flask, request, jsonify, json
from flask_restful import Resource, Api
import bson.json_util

app = Flask(__name__)
api = Api(app)

client = MongoClient('localhost', 27017)


class DatabaseResource(Resource):
    def get(self):
        return client.list_database_names()


class DatabaseNameResource(Resource):
    def get(self, database_name):
        try:
            if database_name not in client.list_database_names():
                raise ValueError(f'Database {database_name} does not exist')
            return client[database_name].list_collection_names()
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class CollectionResource(Resource):
    def get(self, database_name):
        if database_name not in client.list_database_names():
            raise ValueError(f'Database {database_name} does not exist')

        return client[database_name].list_collection_names()


class CollectionNameResource(Resource):
    def get(self, database_name, collection_name):
        try:
            if database_name not in client.list_database_names():
                raise ValueError(f'Database {database_name} does not exist')
            database = client[database_name]
            if collection_name not in database.list_collection_names():
                raise ValueError(f'Table {collection_name} does not exist')

            return bson.json_util.dumps(database[collection_name].find({}))
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class DocumentResource(Resource):
    def get(self, database_name, collection_name):
        try:
            if database_name not in client.list_database_names():
                raise ValueError(f'Database {database_name} does not exist')
            database = client[database_name]
            if collection_name not in database.list_collection_names():
                raise ValueError(f'Table {collection_name} doea not exist')

            return bson.json_util.dumps(list(database[collection_name].find(json.loads(request.args.get('query')))))
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name, collection_name):
        try:
            client[database_name][collection_name].insert_one(json.loads(request.args.get('document')))
            return {'message': 'Document added successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, collection_name):
        try:
            if database_name not in client.list_database_names():
                raise ValueError(f'Database {database_name} does not exist')
            database = client[database_name]
            if collection_name not in database.list_collection_names():
                raise ValueError(f'Table {collection_name} does not exist')

            result = database[collection_name].delete_one(json.loads(request.args.get('query')))
            if result.deleted_count == 0:
                raise ValueError(f"No matching documents found for the query: {json.loads(request.args.get('query'))}")
            return {'message': 'Document deleted successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def put(self, database_name, collection_name):
        try:
            if database_name not in client.list_database_names():
                raise ValueError(f'Database {database_name} does not exist')
            database = client[database_name]
            if collection_name not in database.list_collection_names():
                raise ValueError(f'Table {collection_name} does not exist')

            database[collection_name].update_one(json.loads(request.args.get('query')),
                                                 {"$set": json.loads(request.args.get('update'))})
            return {'message': 'Document updated successfully'}
        except Exception as e:
            traceback.print_exc()
            raise InvalidUsage(str(e), 400)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        result = dict()
        result['message'] = self.message
        return result


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


api.add_resource(DatabaseResource, '/rest/database')
api.add_resource(DatabaseNameResource, '/rest/database/<database_name>')
api.add_resource(CollectionResource, '/rest/database/<database_name>/collection')
api.add_resource(CollectionNameResource, '/rest/database/<database_name>/collection/<collection_name>')
api.add_resource(DocumentResource, '/rest/database/<database_name>/collection/<collection_name>/document')

if __name__ == '__main__':
    app.run(debug=True)
