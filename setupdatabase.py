import sqlite3


sqlcon = sqlite3.connect("database.db")
try:
    sqlcon.execute("drop table meetings")
except sqlite3.OperationalError:
    print("Tabelle meetings existiert noch nicht und wird erstellt")
sqlcon.execute("create table meetings (server integer, channel integer, assignment_name text,id text,dozent text, year integer, month integer, day integer, time integer, link text)")
sqlcon.commit()
sqlcon.close()
print("Datenbank erfolgreich eingerichtet / zurückgesetzt")