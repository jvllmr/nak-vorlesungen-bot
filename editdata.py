import sqlite3, sys
try:
    year=int(input("Jahr?:\n"))
    month=int(input("Monat?:\n"))
    day=int(input("Tag?:\n"))
    time=int(input("Uhrzeit?:\n"))
    newyear=int(input("Neues Jahr?:\n"))
    newmonth=int(input("Neuer Monat?:\n"))
    newday=int(input("Neuer Tag?:\n"))
    newtime=int(input("Neue Uhrzeit?:\n"))
except ValueError:
    print("Das war keine Zahl!")
    sys.exit(1)


sql = sqlite3.connect("database.db")
sql.execute("update meetings set year=?, month=?, day=?, time=? where year=? and month=? and day=? and time=?",(newyear,newmonth,newday,newtime,year,month,day,time))
sql.commit()
sql.close()