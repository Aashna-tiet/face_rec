from os import name
from peewee import *


db = SqliteDatabase('imagesDb.db')


class Data(Model):
    serialNumber = AutoField(PrimaryKeyField)
    name = CharField()
    encodedVector = CharField()
    distance = DoubleField()

    class Meta:
        database = db


db.connect()
db.create_tables([Data])
Data.add_index(SQL('CREATE INDEX idx on Data(distance);'))


def saveData(personName, imageDistance, image_vector):
    data = Data(name=personName,
                distance=imageDistance, encodedVector=image_vector)
    data.save()
    db.close()


def search(ref_distance):
    query = Data.select(Data.distance).where(
        Data.distance > ref_distance-0.00005 and Data.distance < ref_distance+0.00005)
    for person in query:
        return person
