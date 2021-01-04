import sqlite3, os

newdata = sqlite3.connect("newdatabase.db")
olddata = sqlite3.connect("database.db")
newdata.execute("create table meetings (server integer, channel integer, assignment_name text,id text,dozent text, year integer, month integer, day integer, time integer, link text, kennwort text, zenturie text)")
for tobereplaced in olddata.execute("select * from meetings").fetchall():
    newline= list()
    for i in tobereplaced:
        newline.append(i)
    newline.append("A20b")
    newdata.execute("insert into meetings values (?,?,?,?,?,?,?,?,?,?,?,?)",tuple(newline))
newdata.commit()
olddata.close()
newdata.close()

os.replace("newdatabase.db","database.db")