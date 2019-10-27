import traceback

from flask import Flask, render_template, request, flash, url_for, redirect, jsonify, json
from flask_restful import Resource, Api

from database import DBMS, Table, ColumnTypes
from forms import CreateDatabaseForm, EditDatabaseForm, EditTableForm, CreateTableForm, JoinTablesForm, CreateRowForm, \
    UpdateRowForm, DeleteRowForm

app = Flask(__name__)
api = Api(app)

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

_dbms = DBMS.load()


@app.route('/', methods=['GET', 'POST'])
def index():
    edit_database_form = EditDatabaseForm()
    create_database_form = CreateDatabaseForm()
    print('{} {} {} {}'.format(request.method, edit_database_form.is_submitted(), create_database_form.is_submitted(),
                               request.form))

    try:
        if request.method == 'POST':
            if _edit_database_button in request.form:
                print('edit database')
                return redirect(url_for('database', database_name=edit_database_form.database_name.data))
            elif _delete_database_button in request.form:
                print('delete database')
                _dbms.delete_database(edit_database_form.database_name.data)
                flash(f'Database {edit_database_form.database_name.data} was deleted successfully!', 'success')

            if _create_database_button in request.form and create_database_form.validate_on_submit():
                print('create database')
                _dbms.create_database(create_database_form.database_name.data)
                flash(f'Database {create_database_form.database_name.data} was created successfully!', 'success')

        edit_database_form.database_name.choices = list(map(lambda x: (x, x), _dbms.get_databases_names()))
    except Exception as e:
        print('exception: {}'.format(str(e)))
        flash(f'Exception occurred: {str(e)}', 'danger')

    print('get')
    return render_template(_index_template,
                           edit_database_form=edit_database_form,
                           create_database_form=create_database_form)


@app.route('/database/<database_name>', methods=['GET', 'POST'])
def database(database_name: str):
    edit_table_form = EditTableForm()
    create_table_form = CreateTableForm()
    join_tables_form = JoinTablesForm()

    try:
        if request.method == 'POST':
            if _edit_table_button in request.form:
                print('edit table')
                return redirect(url_for('table',
                                        database_name=database_name,
                                        table_name=edit_table_form.table_name.data
                                        ))
            elif _delete_table_button in request.form:
                print('delete table')
                _dbms.get_database(database_name).drop_table(edit_table_form.table_name.data)
                flash(f'Table {create_table_form.table_name.data} successfully deleted', 'success')

            if _create_table_button in request.form and create_table_form.validate_on_submit():
                print('create table')
                _dbms.get_database(database_name).add_table(Table.from_sql(
                    create_table_form.table_name.data,
                    create_table_form.columns_info.data
                ))
                flash(f'Table {create_table_form.table_name.data} successfully created', 'success')

            if _join_tables_button in request.form \
                    and join_tables_form.column_name.validate(join_tables_form) \
                    and join_tables_form.result_name.validate(join_tables_form):
                print('join tables')
                first_table_name = join_tables_form.first_table.data
                second_table_name = join_tables_form.second_table.data
                result_table_name = join_tables_form.result_name.data
                column_name = join_tables_form.column_name.data
                _dbms.get_database(database_name).add_table(
                    _dbms.get_database(database_name).tables[first_table_name].join(
                        _dbms.get_database(database_name).tables[second_table_name],
                        column_name,
                        result_table_name
                    )
                )
                flash(f'Table {first_table_name} and {second_table_name} successfully joined', 'success')

        tables = list(map(lambda x: (x, x), _dbms.get_database(database_name).get_tables_names()))
        edit_table_form.table_name.choices = tables
        join_tables_form.first_table.choices = tables
        join_tables_form.second_table.choices = tables
    except Exception as e:
        print('exception: {}'.format(str(e)))
        flash(f'Exception occurred: {str(e)}', 'danger')
        traceback.print_exc()

    print('get')
    return render_template(_database_template,
                           edit_table_form=edit_table_form,
                           create_table_form=create_table_form,
                           join_tables_form=join_tables_form)


@app.route('/database/<database_name>/table/<table_name>', methods=['GET', 'POST'])
def table(database_name: str, table_name: str):
    print('database name: {}'.format(database_name))
    print('table name: {}'.format(table_name))

    table = _dbms.get_database(database_name).get_table(table_name)

    create_row_form = CreateRowForm()
    update_row_form = UpdateRowForm()
    delete_row_form = DeleteRowForm()

    try:
        if request.method == 'POST':
            if _create_row_button in request.form:
                print('create row')
                table.append_row_sql(create_row_form.row_data1.data)

            if _update_row_button in request.form:
                print('update row')
                table.update_row_sql(update_row_form.row_id1.data, update_row_form.row_data2.data)

            if _delete_row_button in request.form:
                print('delete row')
                table.delete_row(delete_row_form.row_id2.data)
    except Exception as e:
        print('exception: {}'.format(str(e)))
        flash(f'Exception occurred: {str(e)}', 'danger')
        traceback.print_exc()

    print('get')
    return render_template(_table_template,
                           create_row_form=create_row_form,
                           update_row_form=update_row_form,
                           delete_row_form=delete_row_form,
                           table=table,
                           rows=table.rows)


@app.route('/about')
def about():
    return render_template(_about_template)


# -------------------------------------- REST --------------------------------------


class SaveResource(Resource):

    def post(self):
        try:
            _dbms.persist()
            return {'message': 'Databases saved successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)


class DatabaseResource(Resource):

    def get(self):
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
            _dbms.get_database(database_name).add_table(
                Table(
                    table_name,
                    json.loads(request.args.get('column_names')),
                    ColumnTypes.from_json(json.loads(request.args.get('column_types')))
                )
            )
            return {'message': 'Database created successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, table_name):
        try:
            _dbms.get_database(database_name).drop_table(table_name)
            return {'message': 'Database deleted successfully'}
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
            _dbms.get_database(database_name).get_table(table_name).append_row_sql(request.args.get('row_data'))
            return {'message': 'Table row created successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def delete(self, database_name, table_name):
        try:
            _dbms.get_database(database_name).get_table(table_name).delete_row(int(request.args.get('row_id')))
            return {'message': 'Table row deleted successfully'}
        except Exception as e:
            raise InvalidUsage(str(e), 400)

    def put(self, database_name, table_name):
        try:
            print('here')
            _dbms.get_database(database_name).get_table(table_name).update_row_sql(int(request.args.get('row_id')),
                                                                                   request.args.get('row_data'))
            print('here')
            return {'message': 'Table row updated successfully'}
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


api.add_resource(SaveResource, '/rest/save')
api.add_resource(DatabaseResource, '/rest/database')
api.add_resource(DatabaseNameResource, '/rest/database/<database_name>')
api.add_resource(TableResource, '/rest/database/<database_name>/table')
api.add_resource(TableNameResource, '/rest/database/<database_name>/table/<table_name>')
api.add_resource(RowResource, '/rest/database/<database_name>/table/<table_name>/row')

if __name__ == '__main__':
    app.run(debug=True)
