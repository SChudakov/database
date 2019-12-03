import traceback

from flask import Flask, render_template, request, flash, url_for, redirect, jsonify, json

from forms import CreateDatabaseForm, EditDeleteDatabaseForm, EditDeleteTableForm, CreateTableForm, JoinTablesForm, \
    CreateRowForm, \
    UpdateRowForm, DeleteRowForm
from flask_restful import Resource, Api

from database import DBMS, Table, ColumnTypes

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

    return render_template(_table_template,
                           create_row_form=create_row_form,
                           update_row_form=update_row_form,
                           delete_row_form=delete_row_form)


@app.route('/about')
def about():
    return render_template(_about_template)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
