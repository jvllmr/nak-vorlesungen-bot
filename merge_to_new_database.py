import sqlite3, os

newdata = sqlite3.connect("newdatabase.db")
olddata = sqlite3.connect("database.db")
newdata.execute("create table meetings (server integer, channel integer, assignment_name text,id text,dozent text, year integer, month integer, day integer, time integer, link text, kennwort text, zenturie text, fetch_link text)")
for line in olddata.execute("select * from meetings").fetchall():
    newdata.execute("insert into meetings values (?,?,?,?,?,?,?,?,?,?,?,?,?)",line)
newdata.execute("create table bindings (server ingeger, channel integer, zenturie text)")
newdata.commit()
olddata.close()
newdata.close()

os.replace("newdatabase.db","database.db")