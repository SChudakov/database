import traceback

from flask import Flask, render_template, request, flash, url_for, redirect, jsonify, json

from forms import CreateDatabaseForm, EditDeleteDatabaseForm, EditDeleteTableForm, CreateTableForm, JoinTablesForm, \
    CreateRowForm, \
    UpdateRowForm, DeleteRowForm
from flask_restful import Resource, Api

from database import DBMS, Table, ColumnTypes

app = Flask(__name__)
api = Api(app)

_dbms = DBMS.load()

app.config['SECRET_KEY'] = 'ba085e615654d197dbf71c92b5346e48'

_index_template = 'index.html'
_about_template = 'about.html'
_database_template = 'database.html'
_table_template = 'table.html'

_create_database_button = 'create_database'
_delete_database_button = 'delete_database'
_edit_database_button = 'edit_database'

_create_table_button = 'create_table'
_delete_table_button = 'delete_table'
_edit_table_button = 'edit_table'
_join_tables_button = 'join_tables'

_create_row_button = 'create_row'
_update_row_button = 'update_row'
_delete_row_button = 'delete_row'


@app.route('/', methods=['GET', 'POST'])
def index():
    edit_database_form = EditDeleteDatabaseForm()
    create_database_form = CreateDatabaseForm()

    try:
        if request.method == 'POST':
            if _edit_database_button in request.form:
                return redirect(url_for('database', database_name=edit_database_form.edit_delete_database_name.data))

    except Exception as e:
        flash(f'Exception occurred: {str(e)}', 'danger')

    return render_template(_index_template,
                           edit_database_form=edit_database_form,
                           create_database_form=create_database_form)


@app.route('/database/<database_name>', methods=['GET', 'POST'])
def database(database_name: str):
    edit_table_form = EditDeleteTableForm()
    create_table_form = CreateTableForm()
    join_tables_form = JoinTablesForm()

    try:
        if request.method == 'POST':
            if _edit_table_button in request.form:
                return redirect(url_for('table',
                                        database_name=database_name,
                                        table_name=edit_table_form.edit_delete_table_name.data
                                        ))
    except Exception as e:
        flash(f'Exception occurred: {str(e)}', 'danger')

    return render_template(_database_template,
                           edit_table_form=edit_table_form,
                           create_table_form=create_table_form,
                           join_tables_form=join_tables_form)


@app.route('/database/<database_name>/table/<table_name>', methods=['GET'])
def table(database_name: str, table_name: str):
    create_row_form = CreateRowForm()
    update_row_form = UpdateRowForm()
    delete_row_form = DeleteRowForm()

    try:
        if request.method == 'POST':
            if _create_row_button in request.form:
                table.append_row_sql(create_row_form.create_row_data.data)

            if _update_row_button in request.form:
                table.update_row_sql(update_row_form.update_row_id.data, update_row_form.update_row_data.data)

            if _delete_row_button in request.form:
                table.delete_row(delete_row_form.delete_row_id.data)
    except Exception as e:
        flash(f'Exception occurred: {str(e)}', 'danger')

    return render_template(_table_template,
                           create_row_form=create_row_form,
                           update_row_form=update_row_form,
                           delete_row_form=delete_row_form)


@app.route('/about')
def about():
    return render_template(_about_template)


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


api.add_resource(SaveResource, '/rest/save')
api.add_resource(DatabaseResource, '/rest/database')
api.add_resource(DatabaseNameResource, '/rest/database/<database_name>')
api.add_resource(TableResource, '/rest/database/<database_name>/table')
api.add_resource(TableNameResource, '/rest/database/<database_name>/table/<table_name>')
api.add_resource(RowResource, '/rest/database/<database_name>/table/<table_name>/row')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
