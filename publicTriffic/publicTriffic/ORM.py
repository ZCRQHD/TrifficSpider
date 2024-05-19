from peewee import *
import shelve

setting = shelve.open('publicTriffic/db/SQL')
settingDict = setting['db']
db = MySQLDatabase(
    host=settingDict['host'],
    port=settingDict['port'],
    user=settingDict["user"],
    password=settingDict['password'],
    database=settingDict['DBname']

)


class Line(Model):
    id = CharField()
    name = TextField()
    pairCode = CharField()
    preOpen = IntegerField()
    province = TextField()
    city = TextField()
    company = TextField()

    class Meta:
        database = db
        db_table = "line"


class MainStation(Model):
    id = CharField()
    province = TextField()
    city = TextField()
    name = TextField()

    class Meta:
        database = db
        db_table = "mainStation"


class Station(Model):
    id = CharField()
    mainStation = CharField()

    class Meta:
        database = db
        db_table = "station"


class Platform(Model):
    id = CharField()
    station = CharField()
    geox = DoubleField()
    geoy = DoubleField()

    class Meta:
        database = db
        db_table = "platform"


class LineStation(Model):
    line = CharField()
    platform = CharField()

    class Meta:
        database = db
        db_table = "lineStation"


class Path(Model):
    line = CharField()
    geox = DoubleField()
    geoy = DoubleField()

    class Meta:
        database = db
        db_table = "path"
