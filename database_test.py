import json
import unittest

from pathvalidate import ValidationError

from database import Char, TimeInterval, Color, ColorInterval, Time, ColumnTypes, Table, TableRow, Database, DBMS


class CharTest(unittest.TestCase):

    def test_init(self):
        self.assertRaises(ValueError, Char, None)
        self.assertRaises(ValueError, Char, '')
        self.assertRaises(ValueError, Char, 'as')
        self.assertRaises(ValueError, Char, '\l')
        self.assertRaises(ValueError, Char, 'asdlk')

    def test_str(self):
        self.assertEqual('a', str(Char('a')))
        self.assertEqual(' ', str(Char(' ')))
        self.assertEqual('\n', str(Char('\n')))
        self.assertEqual('\t', str(Char('\t')))
        self.assertEqual('\u00df', str(Char('\u00df')))
        self.assertEqual('\u00e4', str(Char('\u00e4')))

    def test_eq(self):
        self.assertEqual(Char('a'), Char('a'))
        self.assertEqual(Char(' '), Char(' '))
        self.assertNotEqual(Char('\n'), Char('s'))
        self.assertNotEqual(Char('p'), Char('\t'))


class ColorTest(unittest.TestCase):
    def test_init(self):
        Color('#000000')
        Color('#ffffff')
        self.assertRaises(ValueError, Color, '')
        self.assertRaises(ValueError, Color, '\n')
        self.assertRaises(ValueError, Color, 'abcdef')
        self.assertRaises(ValueError, Color, '#fffffff')

    def test_eq(self):
        self.assertEqual(Color('#000000'), Color('#000000'))
        self.assertEqual(Color('#ffffff'), Color('#ffffff'))
        self.assertNotEqual(Color('#ffffff'), Color('#000000'))
        self.assertNotEqual(Color('#000000'), Color('#ffffff'))

    def test_str(self):
        self.assertEqual('#000000', str(Color('#000000')))
        self.assertEqual('#ffffff', str(Color('#ffffff')))


class ColorIntervalTest(unittest.TestCase):
    def test_init(self):
        ColorInterval(['#000000', '#ffffff'])
        ColorInterval(['#000000', '#000000'])
        self.assertRaises(ValueError, ColorInterval, ['#ffffff', '#000000'])
        self.assertRaises(ValueError, ColorInterval, ['#000000', 'ffffff'])
        self.assertRaises(ValueError, ColorInterval, ['000000', '#ffffff'])
        self.assertRaises(ValueError, ColorInterval, ['#0000000', '#ffffff'])
        self.assertRaises(ValueError, ColorInterval, ['#0000g0', '#ffffff'])

    def test_eq(self):
        self.assertEqual(ColorInterval(['#000000', '#ffffff']), ColorInterval(['#000000', '#ffffff']))
        self.assertNotEqual(ColorInterval(['#000000', '#ffffff']), ColorInterval(['#000001', '#ffffff']))

    def test_str(self):
        self.assertEqual('["#000000", "#ffffff"]', str(ColorInterval(['#000000', '#ffffff'])))
        self.assertEqual('["#000000", "#000000"]', str(ColorInterval(['#000000', '#000000'])))


class TimeTest(unittest.TestCase):
    def test_init(self):
        Time('11:44:23')
        Time('00:00:00')
        Time('0:0:0')
        Time('23:0:0')
        Time('00:59:59')

        self.assertRaises(ValueError, Time, '00:00:60')
        self.assertRaises(ValueError, Time, '00:60:00')
        self.assertRaises(ValueError, Time, '24:00:00')
        self.assertRaises(ValueError, Time, '24:00:00:4444')
        self.assertRaises(ValueError, Time, '2019-09-28 24:00:00')

    def test_eq(self):
        self.assertEqual(Time('0:0:0'), Time('0:0:0'))
        self.assertEqual(Time('23:0:0'), Time('23:00:00'))
        self.assertNotEqual(Time('23:0:0'), Time('22:0:0'))

    def test_str(self):
        self.assertEqual('23:00:00', str(Time('23:0:0')))
        self.assertEqual('23:00:00', str(Time('23:00:00')))
        self.assertEqual('01:02:03', str(Time('1:2:3')))


class TimeIntervalTest(unittest.TestCase):
    def test_init(self):
        TimeInterval(['17:18:11', '17:18:12'])
        self.assertRaises(ValueError, TimeInterval, ['a', 'b'])
        self.assertRaises(ValueError, TimeInterval, ['17:18:11', ' '])
        self.assertRaises(ValueError, TimeInterval, ['17:18:11', '1711.126812'])
        self.assertRaises(ValueError, TimeInterval, ['17:18:11', '17:18:10'])

    def test_str(self):
        self.assertEqual('["17:18:11", "17:18:11"]', str(TimeInterval(['17:18:11', '17:18:11'])))
        self.assertEqual('["00:00:00", "23:00:00"]', str(TimeInterval(['0:0:0', '23:0:0'])))
        self.assertEqual('["22:00:03", "22:00:04"]', str(TimeInterval(['22:0:3', '22:0:4'])))

    def test_eq(self):
        self.assertEqual(TimeInterval(['17:18:11', '17:18:11']), TimeInterval(['17:18:11', '17:18:11']))
        self.assertNotEqual(TimeInterval(['17:18:11', '17:18:12']), TimeInterval(['17:18:11', '17:18:11']))


class ColumnsTypesTest(unittest.TestCase):

    def test_init(self):
        ColumnTypes([])
        ColumnTypes([int, int, int])
        ColumnTypes([int, float, Char])
        self.assertRaises(ValueError, ColumnTypes, [dict])
        self.assertRaises(ValueError, ColumnTypes, [set])

    def test_to_json(self):
        self.assertEqual(ColumnTypes([]).to_json(), [])
        self.assertEqual(ColumnTypes([int, float, str, Char,
                                      Color, ColorInterval, Time, TimeInterval]).to_json(),
                         ['int', 'real', 'str', 'char', 'color', 'colorinvl', 'time', 'timeinvl'])

    def test_from_json(self):
        self.assertEqual(ColumnTypes.from_json([]), ColumnTypes([]))
        self.assertEqual(
            ColumnTypes.from_json(['int', 'real', 'str', 'char', 'color', 'colorinvl', 'time', 'timeinvl']),
            ColumnTypes([int, float, str, Char, Color, ColorInterval, Time, TimeInterval]))

    def test_convert(self):
        pass

    def test_eq(self):
        self.assertEqual(ColumnTypes([int, float, str, Char, Color, ColorInterval, Time, TimeInterval]),
                         ColumnTypes([int, float, str, Char, Color, ColorInterval, Time, TimeInterval]))
        self.assertNotEqual(ColumnTypes([]),
                            ColumnTypes([int, float, str, Char, Color, ColorInterval, Time, TimeInterval]))

    def test_str(self):
        self.assertEqual(str(ColumnTypes([int, float, str, Char, Color, ColorInterval, Time, TimeInterval])),
                         '''[
    "int",
    "real",
    "str",
    "char",
    "color",
    "colorinvl",
    "time",
    "timeinvl"
]''')


class TableTest(unittest.TestCase):

    def test_join(self):
        table1 = Table('table1', ['c1', 'c2'], ColumnTypes([int, int]))
        table1.append_row([1, 2])
        table1.append_row([1, 4])
        table1.append_row([2, 3])
        table2 = Table('table2', ['c1', 'c3'], ColumnTypes([int, str]))
        table2.append_row([1, 'str1'])
        table2.append_row([2, 'str2'])

        table3 = table1.join(table2, 'c1')

        rows_data = list(map(lambda x: x.data, table3.rows))
        self.assertTrue([1, 2, 'str1'] in rows_data)
        self.assertTrue([1, 4, 'str1'] in rows_data)
        self.assertTrue([2, 3, 'str2'] in rows_data)


class TableRowTest(unittest.TestCase):

    def test_init(self):
        TableRow(0, [])
        self.assertRaises(ValueError, TableRow, -1, [-1])

    def test_to_json(self):
        self.assertEqual({'id': 1, 'data': []}, TableRow(1, []).to_json())

    def test_from_json(self):
        self.assertEqual(TableRow(1, []), TableRow.from_json({'id': 1, 'data': []}, ColumnTypes([])))

    def test_eq(self):
        self.assertEqual(TableRow(0, []), TableRow(0, []))
        self.assertEqual(TableRow(0, [1, 2, 3]), TableRow(0, [1, 2, 3]))
        self.assertNotEqual(TableRow(0, [1]), TableRow(0, [1, 2, 3]))
        self.assertNotEqual(TableRow(0, [1, 2, 3]), TableRow(1, [1, 2, 3]))

    def test_str(self):
        self.assertEqual('''{
    "id": 0,
    "data": [
        "1",
        "2",
        "3"
    ]
}''', str(TableRow(0, [1, 2, 3])))


class DatabaseTest(unittest.TestCase):

    def test_init(self):
        Database('database')
        Database('database database')
        self.assertRaises(ValidationError, Database, 'b??')
        self.assertRaises(ValidationError, Database, 'n/')
        self.assertRaises(ValidationError, Database, 'n/n')
        self.assertRaises(ValidationError, Database, 'n>')

    def test_to_json(self):
        table = Table('table', ['column'], ColumnTypes([str]))
        database = Database('database')
        database.add_table(table)

        self.assertEqual({'name': 'database', 'tables': {'table': table.to_json()}}, database.to_json())

    def test_from_json(self):
        table = Table('table', ['column'], ColumnTypes([str]))
        database = Database('database')
        database.add_table(table)

        self.assertEqual(database, Database.from_json({'name': 'database', 'tables': {'table': table.to_json()}}))


class DBMSTest(unittest.TestCase):
    def test_init(self):
        DBMS('/var/lib/Xdatabse')
        self.assertRaises(ValidationError, DBMS, '/var/lib/Xdatabse??')

    def test_persist(self):
        dbms: DBMS = DBMS()

        db1: Database = dbms.create_database('db1')
        table1 = Table('table1', ['c1', 'c2'], ColumnTypes([int, str]))
        table1.append_row([1, '1'])
        table1.append_row([2, '2'])
        table2 = Table('table2', ['c1', 'c2'], ColumnTypes([str, int]))
        table2.append_row(['1', 1])
        table2.append_row(['2', 2])
        table3 = Table('table3', ['c1', 'c3'], ColumnTypes([int, int]))
        table3.append_row([1, 1])
        table3.append_row([1, 2])
        table3.append_row([2, 1])
        table3.append_row([2, 2])
        db1.add_table(table1)
        db1.add_table(table2)
        db1.add_table(table3)

        db2: Database = dbms.create_database('db2')
        table3 = Table('table3', ['c1', 'c2'], ColumnTypes([Char, Color]))
        table3.append_row([Char('a'), Color('#ffffff')])
        table3.append_row([Char('b'), Color('#aaaaaa')])
        table4 = Table('table4', ['c1', 'c2'], ColumnTypes([Color, Char]))
        table4.append_row([Color('#ffffff'), Char('a')])
        table4.append_row([Color('#ffffff'), Char('a')])
        db2.add_table(table3)
        db2.add_table(table4)

        dbms.persist()
        DBMS.load()
        for database_name in dbms.get_databases_names():
            for table_name, table in dbms.get_database(database_name)._tables.items():
                print(table.to_json())


if __name__ == '__main__':
    unittest.main()
