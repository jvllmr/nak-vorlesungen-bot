import sqlite3,sys

if input("Type in CONFIRM to confirm that you want to reset the entire database: \n") == "CONFIRM":
    pass
else:
    print("Operation abgebrochen")
    sys.exit(0)
sqlcon = sqlite3.connect("database.db")
try:
    sqlcon.execute("drop table meetings")
except sqlite3.OperationalError:
    print("Tabelle meetings existiert noch nicht und wird erstellt")
sqlcon.execute("create table meetings (server integer, channel integer, assignment_name text,id text,dozent text, year integer, month integer, day integer, time integer, link text, kennwort text)")
sqlcon.commit()
sqlcon.close()
print("Datenbank erfolgreich eingerichtet / zurückgesetzt")