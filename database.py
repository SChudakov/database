import os

import json
import re
import shutil
from typing import List, Union, Type, Tuple

from datetime import datetime
import pathvalidate


def assert_exists(path: str) -> None:
    if not os.path.exists(path):
        raise ValueError('Path {} does not exist'.format(path))


def assert_is_dir(path: str) -> None:
    if not os.path.isdir(path):
        raise ValueError('Path {} does not point to a directory'.format(path))


def assert_is_file(path: str) -> None:
    if not os.path.isfile(path):
        raise ValueError('Path {} does not point to a file'.format(path))


class Char:
    def __init__(self, value: str) -> None:
        if not type(value) == str or not len(value) == 1:
            raise ValueError('Invalid char: {}'.format(value))
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Char):
            return self.value == o.value
        return False


class Time:
    time_format = '%H:%M:%S'

    def __init__(self, time: str) -> None:
        self.time = Time.parse_time(time)

    @staticmethod
    def parse_time(time: str):
        return datetime.strptime(time, Time.time_format)

    def __str__(self) -> str:
        return self.time.strftime(Time.time_format)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Time):
            return self.time == o.time
        return False


class Color:
    def __init__(self, color: str) -> None:
        self.color = Color.parse_color(color)

    @staticmethod
    def parse_color(color: str):
        if not len(color) == 7:
            raise ValueError('Color {} format is not correct'.format(color))

        try:
            result = int(color[1:], 16)
        except Exception as e:
            raise ValueError('Color {} format is not correct'.format(color)) from e

        return result

    def __str__(self) -> str:
        return Color.rgb_str(self.color)

    @staticmethod
    def rgb_str(color: int):
        hex_value = hex(color)[2:]
        return '#{}{}'.format('0' * (6 - len(hex_value)), hex_value)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Color):
            return self.color == o.color
        return False


class ColorInterval:

    def __init__(self, value: List[str]) -> None:
        start = Color.parse_color(value[0])
        end = Color.parse_color(value[1])
        if start > end:
            raise ValueError('Start of the color interval {} is greater that its end {}'.format(start, end))

        self.start = start
        self.end = end

    def __str__(self) -> str:
        return json.dumps([Color.rgb_str(self.start), Color.rgb_str(self.end)])

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ColorInterval):
            return self.start == o.start and self.end == o.end
        return False


class TimeInterval:
    def __init__(self, value: List[str]) -> None:
        if not len(value) == 2:
            raise ValueError('Time interval should consist of 2 elements')
        start = datetime.strptime(value[0], Time.time_format)
        end = datetime.strptime(value[1], Time.time_format)
        if start > end:
            raise ValueError('Start {} of the time interval is after its end {}'.format(start, end))
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return json.dumps([self.start.strftime(Time.time_format), self.end.strftime(Time.time_format)])

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TimeInterval):
            return self.start == o.start and self.end == o.end
        return False


RowData = List[Union[int, float, str, Char, Color, ColorInterval, Time, TimeInterval]]
ColumnsTypesStr = List[str]
RowDataStr = List[str]
ColumnsNames = List[str]
ColumnsTypesList = List[Type[Union[int, float, str, Char, Color, ColorInterval, Time, TimeInterval]]]


class ColumnTypes:
    names_to_types = {
        'int': int,
        'real': float,
        'char': Char,
        'str': str,
        'color': Color,
        'colorinvl': ColorInterval,
        'time': Time,
        'timeinvl': TimeInterval
    }

    types_to_names = {
        int: 'int',
        float: 'real',
        str: 'str',
        Char: 'char',
        Color: 'color',
        ColorInterval: 'colorinvl',
        Time: 'time',
        TimeInterval: 'timeinvl'
    }

    def __init__(self, types_list: ColumnsTypesList) -> None:
        for t in types_list:
            if t not in ColumnTypes.types_to_names:
                raise ValueError('{} type is not supported'.format(t))
        self.types_list = types_list

    def to_json(self) -> ColumnsTypesStr:
        return list(map(lambda x: ColumnTypes.types_to_names[x], self.types_list))

    @classmethod
    def from_json(cls, json_obj: ColumnsTypesStr):
        mapped_types = list()
        for type_str in json_obj:
            if type_str not in ColumnTypes.names_to_types:
                raise ValueError(f'Unknown type {type_str}')
            mapped_types.append(ColumnTypes.names_to_types[type_str])
        return cls(mapped_types)

    def convert(self, row: RowDataStr) -> RowData:
        if not len(row) == len(self.types_list):
            raise ValueError('Length of row {} does not match number of columns in the table'.format(row))

        result = list()
        for i in range(len(row)):
            result.append(self.types_list[i](row[i]))

        return result

    def verify(self, row: RowData) -> RowData:
        if not len(row) == len(self.types_list):
            raise ValueError('Length of row {} does not match number of columns in the table'.format(row))

        for i in range(len(row)):
            if not type(row[i]) == self.types_list[i]:
                raise ValueError(f'element {i} in row has invalid type {type(row[i])}; expected: {self.types_list[i]}')

    def convert_column(self, column_index: int, value: str):
        return self.types_list[column_index](value)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ColumnTypes):
            return self.types_list == o.types_list
        return False

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=4)


class TableRow:
    id_field = 'id'
    data_field = 'data'

    def __init__(self, row_id, data: RowData) -> None:
        if row_id < 0:
            raise ValueError('Row id < 0')
        self.id = row_id
        self.data = data

    def to_json(self):
        result = dict()
        result[TableRow.id_field] = self.id
        result[TableRow.data_field] = list(map(str, self.data))
        return result

    @classmethod
    def from_json(cls, json_obj: dict, table_header: ColumnTypes):
        return cls(int(json_obj[TableRow.id_field]), table_header.convert(json_obj[TableRow.data_field]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TableRow):
            return self.id == o.id and self.data == o.data
        return False

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=4)


class Table:
    _name_field = 'name'
    _columns_names_field = 'column_names'
    _columns_types_field = 'columns_types'
    _id_counter_types_field = 'id_counter'
    _rows_field = 'rows'

    def __init__(self, name: str, columns_names: ColumnsNames,
                 column_types: ColumnTypes, id_counter: int = 0) -> None:
        self.name = name
        self.columns_names = columns_names
        self.columns_types = column_types
        self.id_counter = id_counter
        self.rows = list()

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Table):
            return self.name == o.name and self.columns_names == o.columns_names \
                   and self.columns_types == o.columns_types and self.rows == o.rows
        return False

    def __str__(self) -> str:
        return json.dumps(self.to_json(), indent=4)

    def append_row_sql(self, sql: str):
        self.append_row_str(sql.split(','))

    def update_row_sql(self, id: int, sql: str):
        columns_names, column_values = Table._parse_row_sql(sql)
        if id not in [row.id for row in self.rows]:
            raise ValueError(f'No row with id {id}')

        updated_row = None
        for row in self.rows:
            if row.id == id:
                updated_row = row

        for i in range(len(columns_names)):
            columns_name = columns_names[i]
            column_value = column_values[i]
            if columns_name not in self.columns_names:
                raise ValueError(f'No column with name {columns_name} in table {self.name}')
            column_index = self.columns_names.index(columns_name)
            updated_row.data[column_index] = self.columns_types.convert_column(column_index, column_value)

    def delete_row(self, id: int):
        ids = [row.id for row in self.rows]
        if id not in ids:
            raise ValueError(f'No row with id {id} in table {self.name}')
        del self.rows[ids.index(id)]

    def get_row(self, id: int):
        ids = [row.id for row in self.rows]
        if id not in ids:
            raise ValueError(f'No row with id {id} in table {self.name}')
        return self.rows[ids.index(id)]

    @staticmethod
    def _parse_row_sql(sql: str) -> Tuple[List[str], List[str]]:
        split_info = sql.split(',')

        names = list()
        values = list()
        for column_info in split_info:
            column_and_value = column_info.split(':')
            if not len(column_and_value) == 2:
                raise ValueError(f'Invalid format of column-value entry: {column_info}')

            names.append(column_and_value[0])
            values.append(column_and_value[1])

        return names, values

    def append_row_str(self, row_str: RowDataStr):
        converted = self.columns_types.convert(row_str)
        self.append_row(converted)

    def append_row(self, row: RowData):
        self.columns_types.verify(row)
        table_row = TableRow(self.id_counter, row)
        self._append_row_obj(table_row)
        self.id_counter += 1

    def _append_row_obj(self, table_row: TableRow):
        self.rows.append(table_row)

    def to_json(self) -> dict:
        result = dict()
        result[Table._name_field] = self.name
        result[Table._columns_names_field] = self.columns_names
        result[Table._columns_types_field] = self.columns_types.to_json()

        result[Table._rows_field] = list(map(lambda x: x.to_json(), self.rows))

        return result

    @classmethod
    def from_json(cls, json_obj: dict):
        table_header = ColumnTypes.from_json(json_obj[Table._columns_types_field])
        result = cls(json_obj[Table._name_field], json_obj[Table._columns_names_field], table_header)
        id_counter = 0
        for row_json in json_obj[Table._rows_field]:
            table_row = TableRow.from_json(row_json, table_header)
            result._append_row_obj(table_row)
            id_counter = max(id_counter, table_row.id)

        result.id_counter = id_counter + 1
        return result

    @classmethod
    def from_sql(cls, name: str, sql: str):
        names, types = Table._parse_sql(sql)
        return Table(name, names, types)

    @staticmethod
    def _parse_sql(sql: str) -> Tuple[List[str], ColumnTypes]:
        split_info = sql.split(',')

        names = list()
        types = list()
        for column_info in split_info:
            name_and_type = column_info.split()
            if not len(name_and_type) == 2:
                raise ValueError(f'Invalid format of column description: {column_info}'
                                 f', should contain column name and type separated by a space')

            if not re.match('^[a-zA-Z0-9]*$', name_and_type[0]):
                raise ValueError(f'Column name should be alphanumeric string: {name_and_type[0]}')

            names.append(name_and_type[0])
            types.append(name_and_type[1])

        return names, ColumnTypes.from_json(types)

    def join(self, other_table, column_name: str, new_name: str = None):
        if column_name not in self.columns_names:
            raise ValueError('Column {} not present in the {} table'.format(column_name, self.name))
        if column_name not in other_table.columns_names:
            raise ValueError('Column {} not present in the {} table'.format(column_name, other_table.name))

        column_index = self.columns_names.index(column_name)
        other_column_index = other_table.columns_names.index(column_name)

        result_name = '{}JOIN{}'.format(self.name, other_table.name) if new_name is None else new_name

        result_columns_names = list(self.columns_names)
        result_columns_names.extend(other_table.columns_names[:other_column_index])
        result_columns_names.extend(other_table.columns_names[other_column_index + 1:])

        result_columns_types_list = list(self.columns_types.types_list)
        result_columns_types_list.extend(other_table.columns_types.types_list[:other_column_index])
        result_columns_types_list.extend(other_table.columns_types.types_list[other_column_index + 1:])

        result = Table(result_name, result_columns_names, ColumnTypes(result_columns_types_list))

        for row in self.rows:
            for other_row in other_table.rows:
                if row.data[column_index] == other_row.data[other_column_index]:
                    new_row = list(row.data)
                    new_row.extend(other_row.data[other_column_index + 1:])
                    result.append_row(new_row)

        return result


class Database:
    name_field = 'name'
    tables_field = 'tables'

    def __init__(self, name: str) -> None:
        pathvalidate.validate_filename(name)
        self.name = name
        self._tables = dict()

    def get_tables_names(self):
        return list(self._tables.keys())

    def get_table(self, table_name: str):
        if table_name not in self._tables:
            raise ValueError(f'Table with name {table_name} does not exist')
        return self._tables[table_name]

    def add_table(self, table: Table) -> None:
        if table.name in self._tables:
            raise ValueError('Table with name {} already exists in database'.format(table.name))
        self._tables[table.name] = table

    def drop_table(self, name: str) -> None:
        if name not in self._tables:
            raise ValueError('Table with name {} does not exists in the database'.format(name))
        del self._tables[name]

    def to_json(self) -> dict:
        tables = dict()
        for name, table in self._tables.items():
            tables[name] = table.to_json()

        result = dict()
        result[Database.name_field] = self.name
        result[Database.tables_field] = tables

        return result

    @classmethod
    def from_json(cls, json_obj):
        result = cls(json_obj[Database.name_field])
        for name, table_json in json_obj[Database.tables_field].items():
            result._tables[name] = Table.from_json(table_json)
        return result

    @staticmethod
    def load(path: str):
        assert_exists(path)
        assert_is_file(path)

        with open(path) as read_stream:
            json_obj = json.load(read_stream)

            return Database.from_json(json_obj)

    def persist(self, path: str) -> None:
        if os.path.isdir(path):
            raise ValueError(f'Path {path} points to directory')

        with open(path, 'w') as write_stream:
            json.dump(self.to_json(), write_stream, indent=4)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Database):
            return self.name == o.name and self.tables_field == o.tables_field
        return False


class DBMS:
    _default_data_location = '/home/semen/lib/Xdatabse'

    def __init__(self, path: str = _default_data_location) -> None:
        pathvalidate.validate_filepath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self._path = path
        self._databases = dict()

    def create_database(self, name: str):
        if name in self._databases:
            raise ValueError('Database with name {} already exits'.format(name))
        result = Database(name)
        self._databases[name] = result
        return result

    def get_database(self, name: str) -> Database:
        if name not in self._databases:
            raise ValueError('Database with name {} does not exist'.format(name))
        return self._databases[name]

    def delete_database(self, name: str) -> None:
        if name not in self._databases:
            raise ValueError('Database with name {} does not exist'.format(name))
        del self._databases[name]

    def get_databases_names(self):
        return list(self._databases.keys())

    @staticmethod
    def load(path: str = _default_data_location):
        assert_exists(path)
        assert_is_dir(path)

        result = DBMS(path)
        for file_name in os.listdir(path):
            abs_path = os.path.join(path, file_name)
            if os.path.isfile(abs_path):
                result._databases[file_name] = Database.load(abs_path)

        return result

    def persist(self) -> None:
        shutil.rmtree(self._path, ignore_errors=True)
        os.mkdir(self._path)
        for database_name, database in self._databases.items():
            database.persist(os.path.join(self._path, database_name))
