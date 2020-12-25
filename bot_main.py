import discord, sqlite3, asyncio, os, re, datetime
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


class botclient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.assignment_check = self.loop.create_task(self.check_for_next_assignment())
        self.sql = sqlite3.connect("database.db")
        self.sqlbackend = sqlite3.connect("database.db")
        self.prefix = "*"
        self.waitforreaction = dict()
    async def on_ready(self):
        print("Logged on as "+ str(self.user))
        await client.change_presence(status=discord.Status.online, activity=discord.Game(""))
    
    async def on_message(self, message):

        if message.author == self.user:
            return
        
        elif message.content == self.prefix+"upload":

            if not message.attachments:
                await message.add_reaction("\U0000274C")
                await message.channel.send("\U0000274C ***[FAILED]*** Bitte hänge eine Datei an deine Nachricht an")
                return

            else:

                for f in message.attachments:
                    mastermessage = "`\U0001F504 [RUNNING] Lese "+ f.filename + "`\n"
                    currentmessage = await message.channel.send("\U0001F504 ***[RUNNING]*** Lese "+ f.filename)

                    if not ".ics" in f.filename:
                        await message.add_reaction("\U0000274C")
                        await currentmessage.edit(content="\U0000274C ***[FAILED]*** "+f.filename + " ist keine iCalender-Datei")
                        return

                    await f.save(f.filename)
                    localfile = open(f.filename,"rb")
                    icscal = Calendar.from_ical(localfile.read())
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

                            if not module_id:  
                                await message.add_reaction("\U0000274C")
                                await currentmessage.edit(content="\U0000274C ***[FAILED]*** Konnte in "+f.filename+"nicht die Modul-ID vom Termin "+component.get("summary").encode()+" finden")
                                return
                            
                            datetime = str(component.get("DTSTART").dt).split(" ")
                            year = int(datetime[0].split("-")[0])
                            month = int(datetime[0].split("-")[1])
                            day = int(datetime[0].split("-")[2])
                            time = int(datetime[1].split(":")[0] + datetime[1].split(":")[1])
                            data = (message.guild.id,message.channel.id,assignment_name,module_id,dozent,year,month,day,time,"NULL")
                            if self.sql.execute("select * from meetings where server=? and channel=? and assignment_name=? and dozent=? and year=? and month=? and day=? and time=?",(message.guild.id,message.channel.id,assignment_name,dozent,year,month,day, time)).fetchone():
                                print("Meeting "+component.get("summary")+" existiert bereits")
                            else:
                                print("Meeting "+component.get("summary")+" erstellt")
                                self.sql.execute("insert into meetings values (?,?,?,?,?,?,?,?,?,?)", data)
                                self.sql.commit()
                                x = x+1
                    
                    localfile.close()
                    os.remove(f.filename)
                    
                    await message.add_reaction("\U00002705")
                    await currentmessage.edit(content="\U00002705 ***[DONE]*** Erfolgreich "+str(x)+" neue Termine aus der Datei "+f.filename + " migriert")

        elif re.search("^["+self.prefix+"][l][i][n][k]", message.content):
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
            

            currentmessage = await message.channel.send("\U0001F504 ***[RUNNING]*** Setze Links für Meetings mit der Modul-ID "+ module_id)

            if meetings := self.sql.execute("select * from meetings where id=?",(module_id,)).fetchall():
                for compare in meetings:
                    querydata = (compare[0],compare[1],compare[2],module_id,compare[5],compare[6],compare[7],compare[8])
                    if returned_data:=self.sql.execute("select * from meetings where server=? and channel=? and assignment_name=? and id=? and year=? and month=? and day=? and time=?",querydata).fetchall():
                        if len(returned_data) > 1:
                            dozenten= str()
                            dozentenlist = list()
                            x=0
                            for i in returned_data:
                                dozenten = dozenten +symbols[x] + i[4]+ "\n"
                                dozentenlist.append(i[4])
                                x=x+1
                            await currentmessage.edit(content="\U0001F504 ***[RUNNING]*** Für das Modul "+ module_id+" gibt es parallele Termine mit verschiedenen Dozenten. Reagiere auf diese Nachricht mit dem richtigen Emoji, um die bestimmte Vorlesung auszwählen:\n" +dozenten)
                            self.waitforreaction[currentmessage.id]=dict()
                            self.waitforreaction[currentmessage.id]["usermessage"] = message
                            self.waitforreaction[currentmessage.id]["choiceoptions"] = dozentenlist
                            self.waitforreaction[currentmessage.id]["ownmessage"] = currentmessage
                            self.waitforreaction[currentmessage.id]["module_id"] = module_id
                            self.waitforreaction[currentmessage.id]["link"] = link
                            return
                self.sql.execute("update meetings set link=? where id=?",(link,module_id))
                self.sql.commit()
            else:
                await currentmessage.edit(content="\U0000274C ***[FAILED]*** Es gibt kein Modul mit der ID "+module_id)
                await message.add_reaction("\U0000274C")
                
                return

            await message.add_reaction("\U00002705")
            await currentmessage.edit(content="\U00002705 ***[DONE]*** Erfolgreich den Link für das Modul mit der ID " +module_id+ " gesetzt")
            print(str(message.author)+" hat den Link vom Modul "+ module_id+ " auf " + link+ " gesetzt")
            
        elif message.content == self.prefix+"help" or re.search("^[*]$",message.content):
            await message.channel.send("*upload mit iCalendar-Datei im Anhang - Lädt Kalender in die Datenbank des Bots und lässt ihn Benachrichtigungen dazu in diesem Chat schreiben\n*link [Modul-ID] [Link] - Setzt z.B. einen Zoom-Link für eine bestimmte Modul-ID")
            await message.channel.send("GitHub Repo:\nhttps://github.com/kreyoo/nak-vorlesungen-bot")
        
    async def on_reaction_add(self,reaction, user):
        if user == self.user:
            return
        try:
            if self.waitforreaction[reaction.message.id]:
                x=0
                for symbol in symbols:
                    if reaction.emoji==symbol.rstrip(" "):
                        dozent = self.waitforreaction[reaction.message.id]["choiceoptions"][x]
                        message = self.waitforreaction[reaction.message.id]["usermessage"]
                        currentmessage = self.waitforreaction[reaction.message.id]["ownmessage"]
                        module_id = self.waitforreaction[reaction.message.id]["module_id"]
                        link = self.waitforreaction[reaction.message.id]["link"]
                        self.sql.execute("update meetings set link=? where id=? and dozent=?",(link,module_id,dozent))
                        self.sql.commit()
                        await message.add_reaction("\U00002705")
                        await reaction.remove(user)
                        await currentmessage.edit(content="\U00002705 ***[DONE]*** Erfolgreich den Link für das Modul "+module_id+" mit dem Dozenten "+ dozent +  " gesetzt")
                        print(str(user)+" hat den Link vom Modul "+ module_id+ " mit dem Dozenten "+dozent +" auf " + link+ " gesetzt")
                        break
                    x=x+1
                
               
        except KeyError:
            pass

    async def check_for_next_assignment(self):
        await self.wait_until_ready()
        try:
            while not self.is_closed():
                print("Checking for meetings...")
                currenttime = str(datetime.datetime.now()+ datetime.timedelta(minutes = 10))
                time = int(currenttime.split(" ")[1].split(":")[0] + currenttime.split(" ")[1].split(":")[1])
                year = int(currenttime.split(" ")[0].split("-")[0])
                month = int(currenttime.split(" ")[0].split("-")[1])
                day = int(currenttime.split(" ")[0].split("-")[2])
                if meetings:= self.sql.execute("select * from meetings where year=? and month=? and day=? and time=?",(year,month,day,time)).fetchall():
                    for meeting in meetings:
                        guild = self.get_guild(meeting[0])
                        channel = self.get_channel(meeting[1])
                        print("Sende Info zur Vorlesung "+meeting[2])
                        if meeting[9] != "NULL":
                            button = discord.Embed()
                            button.add_field(name="",value="[\U000025B6 Beitreten]("+meeting[9]+")",inline=False)
                            await channel.send("\U00002757 Die Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich.\n Klicke auf den Button um beizutreten:",embed=button)
                        else:
                            await channel.send("\U00002757 Die Vorlesung "+meeting[2]+ " mit "+ meeting[4]+" beginnt gleich")
                await asyncio.sleep(20)
        except Exception:
            self.assignment_check = self.loop.create_task(self.check_for_next_assignment())
            print("Exception occured and caught")


keyfile = open("token.key","r")
token = keyfile.read()
keyfile.close()
client= botclient()
client.run(token)