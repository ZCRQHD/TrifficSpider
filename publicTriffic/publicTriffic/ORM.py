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
    uid = CharField(primary_key=True)
    name = TextField()
    pairCode = CharField()
    preOpen = IntegerField()
    province = TextField()
    city = TextField()
    company = TextField()
    startStation = CharField()
    endStation = CharField()
    path = CharField()

    class Meta:
        database = db
        db_table = "line"




class Platform(Model):
    uid = CharField(primary_key=True)
    geox = DoubleField()
    geoy = DoubleField()
    name = CharField()

    class Meta:
        database = db
        db_table = "platform"


class LineStation(Model):
    line = CharField()
    platform = CharField()

    class Meta:
        primary_key = CompositeKey('line', 'platform')
        database = db
        db_table = "lineStation"


# class Path(Model):
#     line = CharField()
#     geox = DoubleField()
#     geoy = DoubleField()
#     order = IntegerField()
#
#     class Meta:
#         database = db
#         db_table = "path"
db.create_tables([LineStation, Platform, Line])
