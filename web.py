
from flask import Flask, render_template, request, flash, url_for, redirect, jsonify, json
from flask_restful import Api

from database import DBMS, Table
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

    try:
        if request.method == 'POST':
            if _edit_database_button in request.form:
                return redirect(url_for('database', database_name=edit_database_form.database_name.data))
            elif _delete_database_button in request.form:
                _dbms.delete_database(edit_database_form.database_name.data)
                flash(f'Database {edit_database_form.database_name.data} was deleted successfully!', 'success')

            if _create_database_button in request.form and create_database_form.validate_on_submit():
                _dbms.create_database(create_database_form.database_name.data)
                flash(f'Database {create_database_form.database_name.data} was created successfully!', 'success')

        edit_database_form.database_name.choices = list(map(lambda x: (x, x), _dbms.get_databases_names()))
    except Exception as e:
        flash(f'Exception occurred: {str(e)}', 'danger')

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
                return redirect(url_for('table',
                                        database_name=database_name,
                                        table_name=edit_table_form.table_name.data
                                        ))
            elif _delete_table_button in request.form:
                _dbms.get_database(database_name).drop_table(edit_table_form.table_name.data)
                flash(f'Table {create_table_form.table_name.data} successfully deleted', 'success')

            if _create_table_button in request.form and create_table_form.validate_on_submit():
                _dbms.get_database(database_name).add_table(Table.from_sql(
                    create_table_form.table_name.data,
                    create_table_form.columns_info.data
                ))
                flash(f'Table {create_table_form.table_name.data} successfully created', 'success')

            if _join_tables_button in request.form \
                    and join_tables_form.column_name.validate(join_tables_form) \
                    and join_tables_form.result_name.validate(join_tables_form):
                first_table_name = join_tables_form.first_table.data
                second_table_name = join_tables_form.second_table.data
                result_table_name = join_tables_form.result_name.data
                column_name = join_tables_form.column_name.data
                _dbms.get_database(database_name).add_table(
                    _dbms.get_database(database_name).get_table(first_table_name).join(
                        _dbms.get_database(database_name).get_table(second_table_name),
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
        flash(f'Exception occurred: {str(e)}', 'danger')

    return render_template(_database_template,
                           edit_table_form=edit_table_form,
                           create_table_form=create_table_form,
                           join_tables_form=join_tables_form)


@app.route('/database/<database_name>/table/<table_name>', methods=['GET', 'POST'])
def table(database_name: str, table_name: str):
    table = _dbms.get_database(database_name).get_table(table_name)

    create_row_form = CreateRowForm()
    update_row_form = UpdateRowForm()
    delete_row_form = DeleteRowForm()

    try:
        if request.method == 'POST':
            if _create_row_button in request.form:
                table.append_row_sql(create_row_form.row_data1.data)

            if _update_row_button in request.form:
                table.update_row_sql(update_row_form.row_id1.data, update_row_form.row_data2.data)

            if _delete_row_button in request.form:
                table.delete_row(delete_row_form.row_id2.data)
    except Exception as e:
        flash(f'Exception occurred: {str(e)}', 'danger')

    return render_template(_table_template,
                           create_row_form=create_row_form,
                           update_row_form=update_row_form,
                           delete_row_form=delete_row_form,
                           table=table,
                           rows=table.rows)


@app.route('/about')
def about():
    return render_template(_about_template)


if __name__ == '__main__':
    app.run(debug=True)
