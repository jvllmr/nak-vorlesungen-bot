import discord, sqlite3, asyncio, os, re, datetime, requests, codecs, traceback
from icalendar import Calendar


symbols = (
            "\U00000030\U0000FE0F\U000020E3  ",
            "\U00000031\U0000FE0F\U000020E3  ",
            "\U00000032\U0000FE0F\U000020E3  ",
            "\U00000033\U0000FE0F\U000020E3  ",
            "\U00000034\U0000FE0F\U000020E3  ",
            "\U00000035\U0000FE0F\U000020E3  ",
            "\U00000036\U0000FE0F\U000020E3  ",
            "\U00000037\U0000FE0F\U000020E3  ",
            "\U00000038\U0000FE0F\U000020E3  ",
            "\U00000039\U0000FE0F\U000020E3  ",
            )

def timebracket():
    return "["+ datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")+"] "










class botclient(discord.Client):

    async def add_assignments(self, message, sql_object, http_link):
        guild = message.guild
        channel = message.channel
        locationbracket = "["+guild.name + "/"+str(guild.id)+"][" + channel.name +"/"+ str(channel.id) +"]"
        try:
            r = requests.get(http_link)
        except Exception as err:
            await message.add_reaction("\U0000274C")
            await message.channel.send("\U0000274C ***[FAILED]*** Gegebener Link brachte einen Fehler: "+str(err))
            return
        d = r.headers['content-disposition']
        filename = re.findall("filename=(.+)", d)[0]
        mastermessage = "`\U0001F504 [RUNNING] Lese "+ filename + "`\n"
        currentmessage = await message.channel.send("\U0001F504 ***[RUNNING]*** Lese "+ filename)
        
        if not ".ics" in filename:
            await message.add_reaction("\U0000274C")
            await currentmessage.edit(content="\U0000274C ***[FAILED]*** "+ filename + " ist keine iCalender-Datei")
            return
        
        icscal = Calendar.from_ical(codecs.encode(codecs.decode(r.content,encoding="cp1252"),encoding="utf-8"))
        x=0
        for component in icscal.walk():

            if component.name == "VEVENT":
                
                await asyncio.sleep(0.5)
                await currentmessage.edit(content=mastermessage+ "\U0001F504 ***[RUNNING]*** Füge Termin "+ component.get("summary")+ " hinzu")

                for i in component.get("summary").split(","):
                    
                    if regex:=re.search(r"[A-Z]\d\d\d",i):
                        assignment_name = i.lstrip("V")
                        module_id = regex.group()
                        break

                    elif "Zenturienbetreuung" in i:
                        assignment_name = i
                        module_id = "Z"
                        break
                dozent=component.get("summary").split(",")[2]
                zenturie = component.get("summary").split(",")[0]

                if not module_id:  
                    await message.add_reaction("\U0000274C")
                    await currentmessage.edit(content="\U0000274C ***[FAILED]*** Konnte in "+filename+" nicht die Modul-ID vom Termin "+component.get("summary").encode()+" finden")
                    return
                
                datetime = str(component.get("DTSTART").dt).split(" ")
                year = int(datetime[0].split("-")[0])
                month = int(datetime[0].split("-")[1])
                day = int(datetime[0].split("-")[2])
                time = int(datetime[1].split(":")[0] + datetime[1].split(":")[1])
                data = (message.guild.id,message.channel.id,assignment_name,module_id,dozent,year,month,day,time,"NULL","NULL",zenturie,http_link)
                if sql_object.execute("select * from meetings where server=? and channel=? and assignment_name=? and dozent=? and year=? and month=? and day=? and time=?",(message.guild.id,message.channel.id,assignment_name,dozent,year,month,day, time)).fetchone():
                    print(locationbracket+timebracket()+"Meeting "+component.get("summary")+" existiert bereits")
                else:
                    print(locationbracket+timebracket()+"Meeting "+component.get("summary")+" erstellt")
                    sql_object.execute("insert into meetings values (?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
                    sql_object.commit()
                    x = x+1
                
        await message.add_reaction("\U00002705")
        await currentmessage.edit(content="\U00002705 ***[DONE]*** Erfolgreich "+str(x)+" neue Termine aus der Datei "+filename + " migriert")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.assignment_check = self.loop.create_task(self.check_for_next_assignment())
        self.assignment_refresher = self.loop.create_task(self.refresh_assignments())
        self.sql = sqlite3.connect("database.db")
        self.fetch_sql = sqlite3.connect("database.db")
        self.prefix = "_"
        self.waitforreaction = dict()

    async def check_authentication(self, message):
        if message.author.id == message.guild.owner_id or str(message.author) == "krey#6526":
            return True

        for role in message.author.roles:
            if role.name == "NAK_REMINDER":
                return True
        await message.add_reaction("\U0000274C")
        await message.channel.send("\U0000274C Du hast nicht die Berechtigung, um diesen Befehl auszführen.\n Du musst entweder Servereigentümer sein oder eine Rolle Namens NAK_REMINDER innehaben.")
        return False

    async def on_ready(self):
        print(timebracket()+"Logged on as "+ str(self.user))
        await client.change_presence(status=discord.Status.online, activity=discord.Game(""))
    
    async def on_message(self, message):
        guild = message.guild
        channel = message.channel
        locationbracket = "["+guild.name + "/"+str(guild.id)+"][" + channel.name +"/"+ str(channel.id) +"]"
        if message.author == self.user:
            return
        
        elif message.content.split(" ")[0] == self.prefix+"upload":
            if not await self.check_authentication(message):
                return
            elif len(message.content.split(" ")) < 2:
                await message.add_reaction("\U0000274C")
                await message.channel.send("\U0000274C ***[FAILED]*** Bitte gebe einen Link an")
                return

            else:
                http_link = message.content.split(" ")[1]
                
                try:
                    await self.add_assignments(message, self.sql, http_link)
                except Exception as err:
                    await message.add_reaction("\U0000274C")
                    await message.channel.send("\U0000274C ***[FAILED]*** Gegebener Link brachte einen Fehler: "+str(err))
                    print(err)
                    traceback.print_tb(err.__traceback__)
                    return

        elif re.search("^["+self.prefix+"][l][i][n][k]", message.content):
            if not await self.check_authentication(message):
                return
            try:
                module_id = message.content.split(" ")[1]
            except IndexError:
                await message.add_reaction("\U0000274C")
                await message.channel.send("\U0000274C ***[FAILED]*** Bitte gebe eine Modul-ID an")
                
                return
            try:
                link =  message.content.split(" ")[2]
            except IndexError:
                 await message.add_reaction("\U0000274C")
                 await message.channel.send("\U0000274C ***[FAILED]*** Bitte gebe einen Link an")
                 
                 return
            try:
                kennwort =  message.content.split(" ")[3]
            except IndexError:
                kennwort = None

            currentmessage = await message.channel.send("\U0001F504 ***[RUNNING]*** Setze Links für Meetings mit der Modul-ID "+ module_id)

            if meetings := self.sql.execute("select * from meetings where id=?",(module_id,)).fetchall():
                for compare in meetings:
                    querydata = (compare[0],compare[1],compare[2],module_id)
                    if returned_data:=self.sql.execute("select * from meetings where server=? and channel=? and assignment_name=? and id=?",querydata).fetchall():
                        print(returned_data)
                        newreturneddata = list()
                        
                        for checking in returned_data:
                            skip = False
                            for checkdata in newreturneddata:
                                if checkdata[4] == checking[4]:
                                    skip = True
                            if not skip:
                                newreturneddata.append(checking)
                        returned_data = newreturneddata
                        print(returned_data)
                        del newreturneddata
                        if len(returned_data) > 1:
                            dozenten= str()
                            dozentenlist = list()
                            x=0
                            for data in returned_data:
                                dozenten = dozenten +symbols[x] + data[4]+ "\n"
                                dozentenlist.append(data[4])
                                x=x+1
                            await currentmessage.edit(content="\U0001F504 ***[RUNNING]*** Für das Modul "+ module_id+" gibt es Termine mit verschiedenen Dozenten. Reagiere auf diese Nachricht mit dem richtigen Emoji, um die bestimmte Vorlesung auszwählen:\n" +dozenten)
                            self.waitforreaction[currentmessage.id]=dict()
                            self.waitforreaction[currentmessage.id]["usermessage"] = message
                            self.waitforreaction[currentmessage.id]["choiceoptions"] = dozentenlist
                            self.waitforreaction[currentmessage.id]["ownmessage"] = currentmessage
                            self.waitforreaction[currentmessage.id]["module_id"] = module_id
                            self.waitforreaction[currentmessage.id]["link"] = link
                            if kennwort:
                                self.waitforreaction[currentmessage.id]["kennwort"] = kennwort
                            else:
                                self.waitforreaction[currentmessage.id]["kennwort"] = "NULL"

                            return
                if kennwort:
                    self.sql.execute("update meetings set link=?, kennwort=? where id=?",(link,kennwort,module_id))
                else:
                    self.sql.execute("update meetings set link=?, kennwort=? where id=?",(link,"NULL",module_id))
                self.sql.commit()
            else:
                await currentmessage.edit(content="\U0000274C ***[FAILED]*** Es gibt kein Modul mit der ID "+module_id)
                await message.add_reaction("\U0000274C")
                
                return

            await message.add_reaction("\U00002705")
            await currentmessage.edit(content="\U00002705 ***[DONE]*** Erfolgreich den Link für das Modul mit der ID " +module_id+ " gesetzt")
            print(locationbracket+timebracket()+str(message.author)+" hat den Link vom Modul "+ module_id+ " auf \"" + link+ "\" gesetzt")
            
        elif message.content == self.prefix+"help" or re.search("^["+self.prefix+"]$",message.content):
            await message.channel.send("Für diese Befehle wird eine Rolle Namens \"NAK_REMINDER\" benötigt:\n"+self.prefix+"upload mit iCalendar-Datei im Anhang - Lädt Kalender in die Datenbank des Bots und lässt ihn Benachrichtigungen dazu in diesem Chat schreiben\n"+self.prefix+"link [Modul-ID] [Link] - Setzt z.B. einen Zoom-Link für eine bestimmte Modul-ID\n"+self.prefix+"reset löscht alle Termine für den Kanal")
            await message.channel.send("GitHub Repo:\nhttps://github.com/kreyoo/nak-vorlesungen-bot")
        
        elif re.search("^["+self.prefix+"][r][e][s][e][t]", message.content):
            if await self.check_authentication(message):
                currentmessage = await message.channel.send("Bist du dir sicher, dass du alle Termine in diesem Kanal entfernen möchtest? Reagiere mit dem Häkchen-Emoji \U00002705, wenn ja. ")
                self.waitforreaction[currentmessage.id]=dict()
                self.waitforreaction[currentmessage.id]["usermessage"] = message
                self.waitforreaction[currentmessage.id]["ownmessage"] = currentmessage

    async def on_reaction_add(self,reaction, user):
        guild = reaction.message.guild
        channel = reaction.message.channel
        locationbracket = "["+guild.name + "/"+str(guild.id)+"][" + channel.name +"/"+ str(channel.id) +"]"
        if user == self.user:
            return
        try:
            if self.waitforreaction[reaction.message.id]:
                if self.waitforreaction[reaction.message.id]["usermessage"].author != user:
                    return
                try:
                    if self.waitforreaction[reaction.message.id]["link"]:
                        x=0
                        for symbol in symbols:
                            if reaction.emoji==symbol.rstrip(" "):
                                dozent = self.waitforreaction[reaction.message.id]["choiceoptions"][x]
                                message = self.waitforreaction[reaction.message.id]["usermessage"]
                                currentmessage = self.waitforreaction[reaction.message.id]["ownmessage"]
                                module_id = self.waitforreaction[reaction.message.id]["module_id"]
                                link = self.waitforreaction[reaction.message.id]["link"]
                                if self.waitforreaction[reaction.message.id]["kennwort"] != "NULL":
                                    kennwort = self.waitforreaction[reaction.message.id]["kennwort"]
                                    self.sql.execute("update meetings set link=?, kennwort=? where id=? and dozent=?",(link,kennwort,module_id,dozent))
                                else:
                                    self.sql.execute("update meetings set link=?, kennwort=? where id=? and dozent=?",(link,"NULL",module_id,dozent))
                                self.sql.commit()
                                await message.add_reaction("\U00002705")
                                try:
                                    await reaction.remove(user)
                                except discord.errors.Forbidden:
                                    pass
                                await currentmessage.edit(content="\U00002705 ***[DONE]*** Erfolgreich den Link für das Modul "+module_id+" mit dem Dozenten "+ dozent +  " gesetzt")
                                print(locationbracket+timebracket()+str(user)+" hat den Link vom Modul "+ module_id+ " mit dem Dozenten "+dozent +" auf \"" + link+ "\" gesetzt")
                                del self.waitforreaction[reaction.message.id]
                                break
                            x=x+1

                except KeyError:
                    if reaction.emoji=="\U00002705":
                        message = self.waitforreaction[reaction.message.id]["usermessage"]
                        currentmessage = self.waitforreaction[reaction.message.id]["ownmessage"]
                        self.sql.execute("delete from meetings where server=? and channel=?",(message.guild.id,message.channel.id))
                        self.sql.commit()
                        try:
                            await reaction.remove(user)
                        except discord.errors.Forbidden:
                            pass
                        await message.add_reaction("\U00002705")
                        await currentmessage.edit(content="\U00002705 ***[DONE]*** Alle Termine in diesem Kanal gelöscht")
                        print(locationbracket+timebracket()+str(message.author)+" hat alle Termine entfernt")
                        del self.waitforreaction[reaction.message.id]

        except KeyError:
            pass

    async def check_for_next_assignment(self):
        await self.wait_until_ready()
        try:
            while not self.is_closed():
                print(timebracket()+"Starte Meeting-Check...")
                currenttime = str(datetime.datetime.now()+ datetime.timedelta(minutes = 10))
                time = int(currenttime.split(" ")[1].split(":")[0] + currenttime.split(" ")[1].split(":")[1])
                year = int(currenttime.split(" ")[0].split("-")[0])
                month = int(currenttime.split(" ")[0].split("-")[1])
                day = int(currenttime.split(" ")[0].split("-")[2])
                
                if meetings:= self.sql.execute("select * from meetings where year=? and month=? and day=? and time=?",(year,month,day,time)).fetchall():
                    print(timebracket()+"Meetings mit passender Zeit gefunden!")
                    for meeting in meetings:
                        guild = self.get_guild(meeting[0])
                        channel = self.get_channel(meeting[1])
                        locationbracket = "["+guild.name + "/"+str(guild.id)+"][" + channel.name +"/" +str(channel.id) +"]"
                        print(locationbracket+timebracket()+"Sende Info zur Vorlesung "+meeting[2])

                        if "?" in meeting[9]:
                            meeting_id = meeting[9].split("?")[0].split("/j/")[1]
                        
                        elif "/j/" in meeting[9]:
                            meeting_id = meeting[9].split("/j/")[1]
                        else:
                            meeting_id = "Nicht verfügbar"
                        rolle = None
                        for role in guild.roles:
                            if role.name == meeting[11]:
                                rolle = role.mention
                                break

                        if meeting[9] != "NULL" and meeting[10] != "NULL":
                            if "?pwd=" in meeting[9]:
                                link = f"[\U000025B6  Direkt Beitreten]({meeting[9]})"
                            else:
                                link = f"[\U000025B6  Beitreten (Kennwort manuell eingeben)]({meeting[9]})"
                            button = discord.Embed()
                            button.add_field(name="Hier geht es zur Vorlesung:",value=link,inline=False)
                            button.add_field(name="Meeting ID:",value=meeting_id,inline=False)
                            button.add_field(name="Kennwort:",value=meeting[10],inline=False)
                            if rolle:
                                await channel.send(content="\U00002757 "+rolle+"\nDie Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich",embed=button)
                            else:
                                await channel.send(content="\U00002757 Die Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich",embed=button)

                        elif meeting[9] != "NULL" and meeting[10] == "NULL":
                            button = discord.Embed()
                            button.add_field(name="Hier geht es zur Vorlesung:",value="[\U000025B6  Direkt Beitreten]("+meeting[9]+")",inline=False)
                            button.add_field(name="Meeting ID:",value=meeting_id,inline=False)
                            if rolle:
                                await channel.send(content="\U00002757 "+rolle+"\nDie Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich",embed=button)
                            else:
                                await channel.send(content="\U00002757 Die Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich",embed=button)

                        else:
                            if rolle:
                                await channel.send("\U00002757 "+rolle+"\nDie Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich.\n Leider ist noch kein Link zum Meeting hinterlegt.")
                            else:
                                await channel.send("\U00002757 Die Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich.\n Leider ist noch kein Link zum Meeting hinterlegt.")
                                
                print(timebracket()+"Meeting-Check fertig!")
                await asyncio.sleep(60)
        except Exception as err:
            self.assignment_check = self.loop.create_task(self.check_for_next_assignment())
            raise err

    async def refresh_assignments(self):
        # TODO: console debug output
        await self.wait_until_ready()
        try:
            print(timebracket()+"Refetching handler started")
            while not self.is_closed():
                
                nowtime = datetime.datetime.now()
                if int(nowtime.strftime("%H")) == int("00") and nowtime.strftime("%w") == "0" and int(nowtime.strftime("%M")) == int("00"):
                    print(timebracket()+"Refetching the Calendar files")
                    
                    all_meetings = self.fetch_sql.execute("select * from meetings").fetchall()
                    zenturien = dict()
                    channel_ids = list()
                    fetch_links = dict()
                   
                    for meeting in all_meetings:
                        if not meeting[1] in channel_ids:
                            channel_ids.append(meeting[1])
                            fetch_links[meeting[1]] = list()
                            for link in self.fetch_sql.execute("select fetch_link from meetings where channel=?",(meeting[1],)).fetchall():
                                if not link[0] in fetch_links[meeting[1]]:
                                    fetch_links[meeting[1]].append(link[0])
                        try:
                            if zenturien[meeting[11]]:
                                pass
                        except KeyError:
                            zenturien[meeting[11]] = dict()
                    for meeting in all_meetings:
                        
                        try:
                            if zenturien[meeting[11]][meeting[3]]:
                                pass
                        except KeyError:
                            zenturien[meeting[11]][meeting[3]] = dict()
                            for dozent in self.fetch_sql.execute("select dozent from meetings where zenturie=? and id=?",(meeting[11],meeting[3])).fetchall():
                                zenturien[meeting[11]][meeting[3]][dozent[0]] = dict()
                                zenturien[meeting[11]][meeting[3]][dozent[0]]["link"] = meeting[9]
                                zenturien[meeting[11]][meeting[3]][dozent[0]]["kennwort"] = meeting[9]
        
                
                    for channel_id in channel_ids:
                        try:
                            channel = self.get_channel(channel_id)
                            message = await channel.send("\U0001F504 ***[RUNNING]*** Lade Kalenderdateien neu...")
                            for link in fetch_links[channel_id]:
                                self.fetch_sql.execute("delete from meetings where channel=? and fetch_link=?",(channel_id,link))
                                await self.add_assignments(message,self.fetch_sql,link)
                            await message.edit(content="\U0001F504 ***[RUNNING]*** Setze Links wieder neu...")
                            for zenturie in zenturien:
                                for modul in zenturien[zenturie]:
                                    for dozent in zenturien[zenturie][modul]:
                                        self.fetch_sql.execute("update meetings set link=? where zenturie=? and id=? and dozent=?",(zenturien[zenturie][modul][dozent]["link"],zenturie,modul,dozent))
                                        self.fetch_sql.execute("update meetings set kennwort=? where zenturie=? and id=? and dozent=?",(zenturien[zenturie][modul][dozent]["kennwort"],zenturie,modul,dozent))
                            await message.edit(content="\U00002705 ***[DONE]*** Alle Kalenderdateien neu geladen")
                        except Exception as err:
                            self.fetch_sql.rollback()
                            print(err)
                            traceback.print_tb(err.__traceback__)
                            await message.add_reaction("\U0000274C")
                            await message.edit(content="\U0000274C ***[FAILED]*** Es gab einen Fehler: "+str(err))

                await asyncio.sleep(60)
        except Exception as err:
            self.assignment_refresher = self.loop.create_task(self.refresh_assignments())
            print(err)
            traceback.print_tb(err.__traceback__)
            raise err

try:
    keyfile = open("token.key","r")
    token = keyfile.read()
    keyfile.close()
    client= botclient()
    client.run(token)
except FileNotFoundError:
    print("token.key file missing. if this is a test on github. this is ok")
