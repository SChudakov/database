import pymysql
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_hal import link
from flask_hal.document import Document

app = Flask(__name__)
api = Api(app)

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password')
connection.autocommit(True)


class RouteResource(Resource):
    def get(self):
        return Document(links=link.Collection(link.Link('database', '/mysql/database'))).to_dict()


class DatabaseResource(Resource):
    def get(self):
        cursor = connection.cursor()
        cursor.execute('show databases')
        databases = list(map(lambda x: x[0], cursor.fetchall()))
        links = list()
        for database in databases:
            links.append(link.Link(database, f'/mysql/database/{database}'))
        return Document(data={'databases': databases}, links=link.Collection(*links)).to_dict()


class DatabaseNameResource(Resource):
    def get(self, database_name):
        try:
            cursor = connection.cursor()
            cursor.execute('show databases')
            databases = list(map(lambda x: x[0], cursor.fetchall()))
            if database_name in databases:
                return Document(
                    data={'message': f'Database {database_name} exists'},
                    links=link.Collection(link.Link('table', f'/mysql/database/{database_name}/table'))
                ).to_dict()
            else:
                raise ValueError(f'Database {database_name} does not exist')
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name):
        try:
            cursor = connection.cursor()
            cursor.execute(f'CREATE DATABASE {database_name}')
            return Document(data={'message': 'Database created successfully'}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name):
        try:
            cursor = connection.cursor()
            cursor.execute(f'DROP DATABASE {database_name}')
            return Document(data={'message': 'Database deleted successfully'}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class TableResource(Resource):
    def get(self, database_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            cursor.execute('show tables')
            tables = list(map(lambda x: x[0], cursor.fetchall()))
            links = list()
            for table_name in tables:
                links.append(link.Link(table_name, f'/mysql/database/{database_name}/table/{table_name}'))
            return Document(data={'tables': tables}, links=link.Collection(*links)).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class TableNameResource(Resource):
    def get(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            cursor.execute(f'describe {table_name}')
            result = cursor.fetchall()
            return Document(data={'rows': list(result)},
                            links=link.Collection(
                                link.Link('row', f'/mysql/database/{database_name}/table/{table_name}/row'))
                            ).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            description = request.args.get('description')
            cursor.execute(f'create table {table_name} ({description})')
            return Document(data={'message': 'Table created successfully'}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            cursor.execute(f'drop table {table_name}')
            return Document(data={'message': f'Table {table_name} dropped successfully'}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class RowResource(Resource):
    def get(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            cursor.execute(f'select * from {table_name}')
            return Document(data={'rows': list(cursor.fetchall())}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def post(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            values = request.args.get('values')
            cursor.execute(f"insert into {table_name} VALUES ({values})")
            return Document(data={'message': 'Row inserted successfully'}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            where = request.args.get('where')
            cursor.execute(f'delete from {table_name} where {where}')
            return Document(data={'message': 'Rows deleted successfully'}).to_dict()
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def put(self, database_name, table_name):
        try:
            connection.select_db(database_name)
            cursor = connection.cursor()
            set = request.args.get('set')
            where = request.args.get('where')
            cursor.execute(f'update {table_name} set {set} where {where}')
            return Document(data={'message': 'Row updated successfully'}).to_dict()
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


api.add_resource(RouteResource, '/mysql')
api.add_resource(DatabaseResource, '/mysql/database')
api.add_resource(DatabaseNameResource, '/mysql/database/<database_name>')
api.add_resource(TableResource, '/mysql/database/<database_name>/table')
api.add_resource(TableNameResource, '/mysql/database/<database_name>/table/<table_name>')
api.add_resource(RowResource, '/mysql/database/<database_name>/table/<table_name>/row')

if __name__ == '__main__':
    app.run(debug=True)
    connection.close()
