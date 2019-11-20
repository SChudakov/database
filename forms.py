from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Regexp

_alphanumeric_regexp = r'^[\w.@+-]+$'


class EditDeleteDatabaseForm(FlaskForm):
    edit_delete_database_name = SelectField('Database name', choices=[])

    edit_database = SubmitField('Edit Database')


class CreateDatabaseForm(FlaskForm):
    create_database_name = StringField('Database name', validators=[DataRequired(),
                                                                    Length(min=2, max=20),
                                                                    Regexp(_alphanumeric_regexp)])
    create_database = SubmitField('Create Database')


class EditDeleteTableForm(FlaskForm):
    edit_delete_table_name = SelectField('Table name', choices=[])

    edit_table = SubmitField('Edit Table')


class CreateTableForm(FlaskForm):
    create_table_name = StringField('Table name', validators=[DataRequired(),
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
    create_row_data = StringField('Row data', validators=[DataRequired()])
    create_row = SubmitField('Create Row')


class UpdateRowForm(FlaskForm):
    update_row_id = IntegerField('Row id', validators=[DataRequired()])
    update_row_data = StringField('Row data', validators=[])
    update_row = SubmitField('Update Row')


class DeleteRowForm(FlaskForm):
    delete_row_id = IntegerField('Row id', validators=[DataRequired()])
    delete_row = SubmitField('Delete Row')
