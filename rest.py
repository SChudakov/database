import traceback

from flask import Flask, request, jsonify

from flask_restful import Resource, Api

from database import DBMS, Table

app = Flask(__name__)
api = Api(app)

_dbms = DBMS.load()


class SaveResource(Resource):

    def post(self):
        try:
            print("POST TO SAVE")
            _dbms.persist()
            return {'message': 'Databases saved successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class DatabaseResource(Resource):

    def get(self):
        print('GET TO DATABASE')
        return _dbms.get_databases_names()


class DatabaseNameResource(Resource):
    def get(self, database_name):
        try:
            return _dbms.get_database(database_name).to_json()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name):
        try:
            _dbms.create_database(database_name)
            return {'message': 'Database created successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name):
        try:
            _dbms.delete_database(database_name)
            return {'message': 'Database deleted successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class TableResource(Resource):

    def get(self, database_name):
        return _dbms.get_database(database_name).get_tables_names()


class TableNameResource(Resource):
    def get(self, database_name, table_name):
        try:
            return _dbms.get_database(database_name).get_table(table_name).to_json()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name, table_name):
        try:
            print(request.args)
            sql = request.args.get('sql')
            _dbms.get_database(database_name).add_table(
                Table.from_sql(table_name, sql)
            )
            return {'message': 'Database created successfully'}
        except Exception as e:
            traceback.print_exc()
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, table_name):
        try:
            _dbms.get_database(database_name).drop_table(table_name)
            return {'message': 'Table deleted successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class RowResource(Resource):
    def get(self, database_name, table_name):
        try:
            return _dbms.get_database(database_name).get_table(table_name) \
                .get_row(int(request.args.get('row_id'))).to_json()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name, table_name):
        try:
            row = _dbms.get_database(database_name).get_table(table_name).append_row_sql(request.args.get('row_data'))
            return {'message': 'Table row created successfully',
                    'row': row.to_json()}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, table_name):
        try:
            row = _dbms.get_database(database_name).get_table(table_name).delete_row(int(request.args.get('row_id')))
            return {'message': 'Table row deleted successfully',
                    'row': row.to_json()}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def put(self, database_name, table_name):
        try:
            _dbms.get_database(database_name).get_table(table_name).update_row_sql(int(request.args.get('row_id')),
                                                                                   request.args.get('row_data'))
            return {'message': 'Table row updated successfully'}
        except Exception as e:
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


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


api.add_resource(SaveResource, '/rest/save')
api.add_resource(DatabaseResource, '/rest/database')
api.add_resource(DatabaseNameResource, '/rest/database/<database_name>')
api.add_resource(TableResource, '/rest/database/<database_name>/table')
api.add_resource(TableNameResource, '/rest/database/<database_name>/table/<table_name>')
api.add_resource(RowResource, '/rest/database/<database_name>/table/<table_name>/row')

if __name__ == '__main__':
    app.run(debug=True, port=6000)
