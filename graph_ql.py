import graphene
from graphene import Field
from database import DBMS, Table, TableRow

from flask import Flask
from flask_graphql import GraphQLView

_dbms = DBMS.load()


class TableRowType(graphene.ObjectType):
    id = graphene.Int()
    data = graphene.List(graphene.String)


class TableType(graphene.ObjectType):
    name = graphene.String()
    column_names = graphene.List(graphene.String)
    column_types = graphene.List(graphene.String)
    rows = graphene.List(TableRowType)


class Query(graphene.ObjectType):
    table = Field(TableType,
                  database=graphene.String(),
                  table=graphene.String())
    join_tables = Field(TableType,
                        database=graphene.String(),
                        table1=graphene.String(),
                        table2=graphene.String(),
                        column_name=graphene.String(),
                        num_rows=graphene.Int(),
                        result_table_name=graphene.String(required=False))

    def resolve_table(self, info, database, table):
        return Query.form_table_type(
            _dbms.get_database(database).get_table(table).to_json())

    def resolve_join_tables(self,
                            info,
                            database,
                            table1,
                            table2,
                            column_name,
                            result_table_name=None):
        database = _dbms.get_database(database)
        table1 = database.get_table(table1)
        table2 = database.get_table(table2)
        result_table = table1.join(table2, column_name, result_table_name)

        return Query.form_table_type(result_table.to_json())

    @staticmethod
    def form_table_type(table_json):
        return TableType(
            name=table_json[Table.name_field],
            column_names=table_json[Table.columns_names_field],
            column_types=table_json[Table.columns_types_field],
            rows=list(
                map(lambda row_json:
                    TableRowType(id=row_json[TableRow.id_field],
                                 data=row_json[TableRow.data_field]),
                    table_json[Table.rows_field])
            ),
        )


schema = graphene.Schema(query=Query)

app = Flask(__name__)
app.debug = True

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

if __name__ == '__main__':
    app.run(debug=True)
