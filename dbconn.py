import pymysql

cnx = pymysql.connect(user='user1', password='passw0rd.', database='frec_db')

cr = cnx.cursor()

add_entry = ("INSERT INTO face_encodings"
             "(person_name,image_path, face_enc, ref_dist)"
             "VALUES (%(person_name)s, %(image_path)s, %(face_enc)s, %(ref_dist)s)")

data_val = {
    'person_name': 'Aashna',
    'image_path': '/home/user/pictures',
    'face_enc': '12 23 34 45 56 67 78',
    'ref_dist': 123,
}

cr.execute(add_entry, data_val)
cnx.commit()

cr.close()
cnx.close()
