import sqlite3, os

newdata = sqlite3.connect("newdatabase.db")
olddata = sqlite3.connect("database.db")

for tobereplaced in olddata.execute("select * from meetings").fetchall():
    newline= list()
    for i in tobereplaced:
        newline.append(i)
    newline.append("NULL")
    newdata.execute("insert into meetings values (?,?,?,?,?,?,?,?,?,?,?)",tuple(newline))
newdata.commit()
olddata.close()
newdata.close()

os.replace("newdatabase.db","database.db")