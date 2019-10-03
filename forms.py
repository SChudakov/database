from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextField, IntegerField
from wtforms.validators import DataRequired, Length, Regexp

_alphanumeric_regexp = r'^[\w.@+-]+$'


class EditDatabaseForm(FlaskForm):
    database_name = SelectField('Database name', choices=[])

    edit_database = SubmitField('Edit Database')
    delete_database = SubmitField('Delete Database')


class EditTableForm(FlaskForm):
    table_name = SelectField('Table name', choices=[])

    edit_table = SubmitField('Edit Table')
    delete_table = SubmitField('Delete Table')


class CreateDatabaseForm(FlaskForm):
    database_name = StringField('Database name', validators=[DataRequired(),
                                                             Length(min=2, max=20),
                                                             Regexp(_alphanumeric_regexp)])
    create_database = SubmitField('Create Database')


class CreateTableForm(FlaskForm):
    table_name = StringField('Table name', validators=[DataRequired(),
                                                       Length(min=2, max=20),
                                                       Regexp(_alphanumeric_regexp)])
    columns_info = StringField('Columns info')
    create_table = SubmitField('Create Table')


class JoinTablesForm(FlaskForm):
    first_table = SelectField('First table', choices=[])
    second_table = SelectField('Second table', choices=[])

    column_name = StringField('Field name', validators=[DataRequired(),
                                                        Length(min=2, max=20),
                                                        Regexp(_alphanumeric_regexp)])
    result_name = StringField('Result table name', validators=[DataRequired(),
                                                               Length(min=2, max=20),
                                                               Regexp(_alphanumeric_regexp)])
    join_tables = SubmitField('Join Tables')


class CreateRowForm(FlaskForm):
    row_data1 = StringField('Row data', validators=[DataRequired()])
    create_row = SubmitField('Create Row')


class UpdateRowForm(FlaskForm):
    row_id1 = IntegerField('Row id', validators=[DataRequired()])
    row_data2 = StringField('Row data', validators=[])
    update_row = SubmitField('Update Row')


class DeleteRowForm(FlaskForm):
    row_id2 = IntegerField('Row id', validators=[DataRequired()])
    delete_row = SubmitField('Delete Row')


class SaveForm:
    save = SubmitField('Save')
