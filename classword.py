from urllib import request
from urllib import error
from bs4 import BeautifulSoup
from bs4 import NavigableString
from functools import lru_cache
from discord import Embed
from discord import Colour

class Word:
    #Default Constructor
    def __init__(self):
        """Default Constructor"""
        self.name = "" #Store the Word
        self.partofspeech = "" #Part of Speech of a Word
        self.meanings = [] #List of {'meaning', 'example'}
        self.idioms = [] #List of {'idiom', 'mean', 'example'}
        self.nearbywords = [] #List of Nearby Words
        self.synonyms = [] #List of Synonyms
        self.antonyms = [] #List of Antonyms
        self.phrasalverbs = [] #List of Phrasal Verbs
        self.soup = None #Soup Object of the WebPage

    #GetSet - Name
    def setname(self, nm):
        """Sets the name of the word"""
        self.name = nm.capitalize()
    def getname(self):
        """Returns the name of the word"""
        return self.name

    #GetSet - Part Of Speech
    def setpartofspeech(self, pos):
        """Sets the part of speech of the word"""
        self.partofspeech = pos.capitalize()
    def getpartofspeech(self):
        """Returns the part of speech of the word"""
        return self.partofspeech

    #GetAdd - Meaning
    def addmeaning(self, *args):
        """Adds a meaning to the self.meaning list, args[0] is meaning, args[1] are examples"""
        meaningdict = {"meaning":args[0], "examples":args[1]}
        self.meanings.append(meaningdict)
    def getmeanings(self):
        """Returns the meanings of the word"""
        return self.meanings

    #GetAdd - Idioms
    def addidiom(self, *args):
        """Adds an idiom to the self.idioms list, args[0] is the idiom, args[1] is its meaning and args[2] are examples"""
        idiomdict = {"idiom":args[0], "meaning":args[1], "examples":args[2]}
        self.idioms.append(idiomdict)
    def getidioms(self):
        """Returns the idoms for the word"""
        return self.idioms

    #GetAdd - Nearby Words
    def addnearbyword(self, nbword):
        """Adds a nearby word to self.nearbywords"""
        self.nearbywords.append(nbword)
    def getnearbywords(self):
        """Get the nearby words of the given Word"""
        return self.nearbywords

    #GetAdd - Synonyms
    def addsynonym(self, syn):
        """Adds a synonym of the word to self.synonyms"""
        self.synonyms.append(syn)
    def getsynonyms(self):
        """Returns the synonyms of the word"""
        return self.synonyms

    #GetAdd - Antonyms
    def addantonym(self, ant):
        """Adds an antonym of the word to self.antonyms"""
        self.antonyms.append(ant)
    def getantonyms(self):
        """Returns the antonyms of the word"""
        return self.antonyms

    #GetAdd - Phrasal Verbs
    def addphrasalverb(self, pv):
        """Adds a phrasal verb of the word to self.phrasalverbs"""
        self.phrasalverbs.append(pv)
    def getphrasalverbs(self):
        """Returns the phrasal verbs of the word."""
        return self.phrasalverbs

    #Get Html Script, cached.
    @lru_cache(maxsize=100)
    def gimmehtml(self, url):
        """Returns the html page of the url"""
        req = request.urlopen(url)
        html = req.read().decode("utf8")
        req.close()
        return html
    #Get Url
    def geturl(self):
        nm = self.name
        #Word must be 'word', not 'Word'
        if nm[0].isupper():
            nm = nm.lower()

        #That's the url
        url = 'https://www.oxfordlearnersdictionaries.com/definition/english/' + nm
        return url
    #Check Existence
    def checkexistence(self):
        """Returns True/False according to the existence of the webpage"""
        try:
            nm = self.name
            #Word must be 'word', not 'Word'
            if nm[0].isupper():
                nm = nm.lower()

            #That's the url
            url = 'https://www.oxfordlearnersdictionaries.com/definition/english/' + nm

            #Trying to get the website
            h = self.gimmehtml(url)
        except error.HTTPError:
            #Couldn't find the website
            return False
        #If flow of control got till here, no HTTPError occured.
        return True
    #Create Soup
    def generatesoup(self):
        """Generates the Beautiful Soup object for the given word"""

        nm = self.name
        #Word must be 'word', not 'Word'
        if nm[0].isupper():
            nm = nm.lower()

        #That's the url
        url = 'https://www.oxfordlearnersdictionaries.com/definition/english/' + nm

        #Perfect time to make soup
        self.soup = BeautifulSoup(self.gimmehtml(url), 'html.parser')
    #Get soup
    def getsoup(self):
        """Gets the soup object for the word"""
        return self.soup

    #Main stuff, Fill the parameters of the word
    def fillparams(self):
        """Fills the parameters of the word"""
        #Word Name
        self.setname(self.getsoup().h2.text)

        #Word Part of Speech
        self.setpartofspeech(self.getsoup().find("span", {"class":"pos"}).text)

        #Word Meanings
        #A small function to suit our needs
        def checkparents(x):
            """Checks if there's collapse or snippet as parent, i.e., if it goes to Oxford Collocations Dictionary."""
            if (x.find_parent("span", {"class":"collapse"}) or x.find_parent("span", {"class":"snippet"}) or x.find_parent("span", {"class":"x-g"})):
                #Wrong place!
                return False
            else:
                return True
        #Case 1 - Has Multiple Meanings.
        if(self.getsoup().find("ol", {"class":"h-g"})):
            #We notice that <ol class="h-g"> is present only in multi meaning cases.

            meaningcontainer = self.getsoup().select("ol[class=h-g] > span[class=sn-gs]") #A list holding all the meanings.
            if len(meaningcontainer) == 1: #Multi line without header
                meaningcontainer = self.getsoup().find("span", {"class":"sn-gs"}).findAll("li", {"class":"sn-g"})

            #Doing this for same header, multiple <li> tags and modifying meaningcontainer
            index = 0
            for x in meaningcontainer:
                if(len(x.select("span[class=sn-gs] > li[class=sn-g]")) >= 2):
                    #This meaning has more than two <li> tags
                    if(x.find("span", {"class":"shcut"})):
                        #Contains a header that needs to be handled.
                        #We join in the header to the first <li> tag.
                        toberemoved = x.find("span", {"class":"shcut"})
                        shcuttag = toberemoved.extract()
                        x.findAll("li", {"class":"sn-g"})[0].insert(1, shcuttag)

                    #The <li> tags
                    litags = x.findAll("li", {"class":"sn-g"})
                    #Let's pop out current one!
                    meaningcontainer.pop(index)
                    #And now we should add!
                    meaningcontainer[index:index] = litags
                    index += len(litags)
                else:
                    index += 1

            for item in meaningcontainer:
                #Will loop through the 'li' tags
                means = "" #The String holding the meaning.

                #Has Header
                if(item.find("span", {"class":"shcut"})):
                    if(checkparents(item.find("span", {"class":"shcut"}))):
                        means += "[" + item.find("span", {"class":"shcut"}).text.strip().capitalize() + "]: "

                #Has Usage
                if(item.find("span", {"class":"use"})):
                    if(checkparents(item.find("span", {"class":"use"}))):
                        means += item.find("span", {"class":"use"}).text.strip().capitalize() + " "

                #Has a strong text
                if(item.find("span", {"class":"v"})):
                    if(checkparents(item.find("span", {"class":"v"}))):
                        means += item.find("span", {"class":"v"}).text.strip().capitalize() + ", "

                #Has a third bracket [transitive, uncountable] stuff in front of actual meaning.
                if (item.find("span", {"class":"gram-g"})):
                    if(checkparents(item.find("span", {"class":"gram-g"}))):
                        means += item.find("span", {"class":"gram-g"}).text.strip() + " "

                #Has a bracketed label
                if (item.find("span", {"class":"label-g"})):
                    if(checkparents(item.find("span", {"class":"label-g"}))):
                        means += item.find("span", {"class":"label-g"}).text.strip() + " " #format - (label)

                #Has a bolded definition before the actual meaning.
                if (item.find("span", {"class":"cf"})):
                    if(checkparents(item.find("span", {"class":"cf"}))):
                        means += item.find("span", {"class":"cf"}).text.strip().capitalize() + " - "

                #The actual meaning.
                if(item.find("span", {"class":"def"})):
                    means += item.find("span", {"class":"def"}).text.strip().capitalize()


                #Examples
                examplecontainer = item.findAll("span", {"class":"x-g"}) #A list holding all the examples.
                egs = "" #The String holding the examples under that meaning.
                c = 0

                for egitem in examplecontainer:
                    #Will loop through the example list
                    thiseg = "" #The string holding this example

                    #Don't hold more than 5 examples
                    c += 1
                    if c>5:
                        break

                    #Has some third bracketed stuff prior to the original example
                    if(egitem.find("span", {"class":"gram-g"})):
                        thiseg += egitem.find("span", {"class":"gram-g"}).text.strip() + "  "

                    #Has a bracketed label
                    if (egitem.find("span", {"class":"label-g"})):
                        thiseg += egitem.find("span", {"class":"label-g"}).text.strip() + " " #format - (label)

                    #Has a bolded text in front of the original example
                    if(egitem.find("span", {"class":"cf"})):
                        thiseg += egitem.find("span", {"class":"cf"}).text.strip().capitalize() + " - "

                    #The actual example
                    if(egitem.find("span", {"class":"x"})):
                        thiseg += egitem.find("span", {"class":"x"}).text.strip().capitalize()

                    egs += "\neg: " + thiseg

                #Now, 'means' holds a meaning of the word and 'egs' holds the related examples to the meaning.
                #So, let's add it!
                if (means.strip() != ''):
                    self.addmeaning(means, egs)

                #LetsCheck - Synonyms and Antonyms
                if(item.find("span", {"class":"xr-gs"})):
                    if(checkparents(item.find("span", {"class":"xr-gs"}))):
                        lolcontainer = item.findAll("span", {"class":"xr-gs"})
                        for lol in lolcontainer:
                            #Loops through the entries.
                            lolvar = ""
                            if lol.select("span[class=xr-gs] > span[class=prefix]"):
                                lolvar = lol.select("span[class=xr-gs] > span[class=prefix]").text.strip()

                            if lolvar == 'synonym':
                                self.addsynonym(lol.find("span", {"class":"xh"}).text.strip().capitalize())

                            if lolvar == 'opposite':
                                self.addantonym(lol.find("span", {"class":"xh"}).text.strip().capitalize())
        #Case 2 - Has only one meaning.
        if(self.getsoup().find("span", {"class":"sn-g"})):

            item = self.getsoup().find("span", {"class":"sn-g"}) #Storing the meaning item
            means = "" #The String holding the meaning.

            #Has Header
            if(item.find("span", {"class":"shcut"})):
                if(checkparents(item.find("span", {"class":"shcut"}))):
                    means += "[" + item.find("span", {"class":"shcut"}).text.strip().capitalize() + "]: "

            #Has Usage
            if(item.find("span", {"class":"use"})):
                if(checkparents(item.find("span", {"class":"use"}))):
                    means += item.find("span", {"class":"use"}).text.strip().capitalize() + " "

            #Has a strong text
            if(item.find("span", {"class":"v"})):
                if(checkparents(item.find("span", {"class":"v"}))):
                    means += item.find("span", {"class":"v"}).text.strip().capitalize() + ", "

            #Has a third bracket [transitive, uncountable] stuff in front of actual meaning.
            if (item.find("span", {"class":"gram-g"})):
                if(checkparents(item.find("span", {"class":"gram-g"}))):
                    means += item.find("span", {"class":"gram-g"}).text.strip() + " "

            #Has a bracketed label
            if (item.find("span", {"class":"label-g"})):
                if(checkparents(item.find("span", {"class":"label-g"}))):
                    means += item.find("span", {"class":"label-g"}).text.strip() + " " #format - (label)

            #Has a bolded definition before the actual meaning.
            if (item.find("span", {"class":"cf"})):
                if(checkparents(item.find("span", {"class":"cf"}))):
                    means += item.find("span", {"class":"cf"}).text.strip().capitalize() + " - "

            #The actual meaning.
            if(item.find("span", {"class":"def"})):
                means += item.find("span", {"class":"def"}).text.strip().capitalize()


            #Examples
            examplecontainer = item.findAll("span", {"class":"x-g"}) #A list holding all the examples.
            egs = "" #The String holding the examples under that meaning.
            c=0

            for egitem in examplecontainer:
                #Will loop through the example list
                thiseg = "" #The string holding this example

                #Don't hold more than 5 examples
                c += 1
                if c>5:
                    break

                #Has some third bracketed stuff prior to the original example
                if(egitem.find("span", {"class":"gram-g"})):
                    thiseg += egitem.find("span", {"class":"gram-g"}).text.strip() + "  "

                #Has a bracketed label
                if (egitem.find("span", {"class":"label-g"})):
                    thiseg += egitem.find("span", {"class":"label-g"}).text.strip() #format - (label)

                #Has a bolded text in front of the original example
                if(egitem.find("span", {"class":"cf"})):
                    thiseg += egitem.find("span", {"class":"cf"}).text.strip().capitalize() + " - "

                #The actual example
                if (egitem.find("span", {"class":"x"})):
                    thiseg += egitem.find("span", {"class":"x"}).text.strip().capitalize()

                egs += "\neg: " + thiseg

            #Now, 'means' holds a meaning of the word and 'egs' holds the related examples to the meaning.
            #So, let's add it!
            if (means.strip() != ''):
                self.addmeaning(means, egs)

            #LetsCheck - Synonyms and Antonyms
            if(item.find("span", {"class":"xr-gs"})):
                if(checkparents(item.find("span", {"class":"xr-gs"}))):
                    lolcontainer = item.findAll("span", {"class":"xr-gs"})
                    for lol in lolcontainer:
                        #Loops through the entries.
                        lolvar = ""
                        if lol.select("span[class=xr-gs] > span[class=prefix]"):
                            lolvar = lol.select("span[class=xr-gs] > span[class=prefix]").text.strip()

                        if lolvar == 'synonym':
                            self.addsynonym(lol.find("span", {"class":"xh"}).text.strip().capitalize())

                        if lolvar == 'opposite':
                            self.addantonym(lol.find("span", {"class":"xh"}).text.strip().capitalize())

        #Word Idioms
        #Case 1- No Idioms
        if(not self.getsoup().find("span", {"class":"idm-gs"})):
            pass
        #Case 2- Has Idioms
        else:
            idiomcontainer = self.getsoup().findAll("span", {"class":"idm-g"})
            for thisidiom in idiomcontainer:
                #Loops over the idiom groups.

                #Idiom
                idiomname = thisidiom.find("span", {"class":"idm"}).text.strip().capitalize()


                #Meaning
                idiommeaning = ""
                #If has a third bracket [transitive, uncountable] stuff in front
                if (thisidiom.find("span", {"class":"gram-g"})):
                    idiommeaning += item.find("span", {"class":"gram-g"}).text.strip() + "  "
                #If has label
                if (thisidiom.find("span", {"class":"label-g"})):
                    idiommeaning += thisidiom.find("span", {"class":"label-g"}).text.strip().capitalize() + " "
                #Has a bolded definition before the meaning
                if (thisidiom.find("span", {"class":"cf"})):
                    idiommeaning += item.find("span", {"class":"cf"}).text.strip() + " - "
                #The actual meaning
                if (thisidiom.find("span", {"class":"def"})):
                    idiommeaning += thisidiom.find("span", {"class":"def"}).text.strip().capitalize()


                #Examples
                egcontainer = thisidiom.findAll("span", {"class":"x-g"})
                idiomegs = ""
                c=0
                for egitem in egcontainer:
                    #Loops over the examples
                    thiseg = "" #The string holding this example
                    #Don't hold more than 5 examples
                    c += 1
                    if c>5:
                        break
                    #Has some third bracketed stuff prior to the original example
                    if(egitem.find("span", {"class":"gram-g"})):
                        thiseg += egitem.find("span", {"class":"gram-g"}).text.strip() + "  "
                    #Has a bracketed label
                    if (egitem.find("span", {"class":"label-g"})):
                        thiseg += "(" + egitem.find("span", {"class":"label-g"}).text.strip() + ") " #format - (label)
                    #Has a bolded text in front of the original example
                    if(egitem.find("span", {"class":"cf"})):
                        thiseg += egitem.find("span", {"class":"cf"}).text.strip().capitalize() + " - "
                    #The actual example
                    thiseg += egitem.find("span", {"class":"x"}).text.strip().capitalize()

                    idiomegs += "\neg: " + thiseg

                #Now, 'idiomname' holds the idiom, 'idiommeaning' holds its meaning and 'idiomegs' holds the examples.
                #So, let's add them!
                self.addidiom(idiomname, idiommeaning, idiomegs)

        #Nearby Words
        nearbycontainer = self.getsoup().find("div", {"class":"responsive_row nearby"}).findAll("li")
        for nearword in nearbycontainer:
            #Loops over nearby <li> tags
            thisnear = ""

            #Taking hold of the <data class="hwd"> because impotant stuff's in there.
            entry = nearword.find("data", {"class":"hwd"})

            #Finding the word.
            for w in entry.contents:
                if isinstance(w, NavigableString):
                    thisnear += w.strip().capitalize()

            #Checking is <pos> is there for part of speech and adding if present
            if(entry.find("pos")):
                thisnear += ", " + entry.find("pos").text.strip().capitalize()

            #NearbyWord is ready at 'thisnear'
            #So, let's add it!
            self.addnearbyword(thisnear)

        #Phrasal Verbs
        checkvar = len(self.getsoup().findAll("dd"))
        if checkvar >= 2:
            #Phrasal Verbs are present.
            pvcontainer = self.getsoup().findAll("dd")[1].findAll("li")
            for thispv in pvcontainer:
                #Loops through the phrasal verbs
                pv = thispv.get_text().strip().rsplit(' ', 2)
                pvtext = ""
                if pv[1].lower().strip() == 'phrasal' and pv[2].lower().strip() == 'verb':
                    pvtext = pv[0]
                else:
                    pvtext = ' '.join(pv)
                self.addphrasalverb(pvtext.strip().capitalize())

        #Synonyms
        if(self.getsoup().find("span", {"title":"Synonyms"})):
            #Has Synonyms
            syncontainter = self.getsoup().find("span", {"title":"Synonyms"}).find("span", {"class":"inline"}).findAll("span", {"class":"li"})
            for syn in syncontainter:
                #Loops over the synonyms
                self.addsynonym(syn.get_text().strip().capitalize())

        #Antonyms
        if(self.getsoup().find("span", {"title":"Opposite"})):
            #Has Antonyms
            antcontainter = self.getsoup().find("span", {"title":"Opposite"}).find("span", {"class":"inline"}).findAll("span", {"class":"li"})
            for ant in antcontainter:
                #Loops over the antonyms
                self.addantonym(ant.get_text().strip().capitalize())

    #PrintingEverything - For Self Check
    def displayeverything(self):
        """Prints Out everything to the console"""
        print ("Word Name > {} \n".format(self.getname()))
        print ("Part of Speech > {}\n".format(self.getpartofspeech()))
        for mean in self.getmeanings():
            print ("Meaning > {} \nExamples > {}\n".format(mean["meaning"], mean["examples"]))
        for idm in self.getidioms():
            print ("Idiom > {}\nMeans > {}\nExamples > {}\n".format(idm["idiom"], idm["meaning"], idm["examples"]))
        for syn in self.getsynonyms():
            print ("Synonym > {}\n".format(syn))
        for atm in self.getantonyms():
            print ("Antonym > {}\n".format(atm))
        for nw in self.getnearbywords():
            print ("Nearby Word > {}\n".format(nw))
        for pv in self.getphrasalverbs():
            print ("Phrasal Verb > {}\n".format(pv))

    #Return Embed(s)
    def return_embeds(self, context):
        """Returns the Embeds [] of Embeds

        if checkexistence() == True:
            Starting Embed :-
            1. Author Name = self.getname()
            2. Thumbnail = 'https://global.oup.com/academic/covers/pop-up/9780191836718'
            3. Footer Text = 'Requested by ' + context.message.author.nick + ' | Page ' + 1
            4. Footer Icon Url = context.message.author.default_avatar_url
            5. Description = "Part of Speech = **" + self.getpartofspeech() + "**\nClick [here](" + self.geturl() + ") to go to the `Oxford 3000` page of *" + self.getname() + "*"
            6. Add fields for Phrasal Verbs, Synonyms, Antonyms and Nearby Words.

            Meaning Embed :-
            1. Author Name = 'Meanings for ' + self.getname()
            2. Footer Text = 'Requested by ' + context.message.author.nick + ' | Page ' + 2
            3. Footer Icon Url = context.message.author.default_avatar_url
            4. Description = '*are as follows :*'
            5. Add fields for Meanings.

            Idiom Embed :- (if)
            1. Author Name = 'Idioms for ' + self.getname()
            2. Footer Text = 'Requested by ' + context.message.author.nick + ' | Page ' + 3
            3. Footer Icon Url = context.message.author.default_avatar_url
            4. Description = '*are as follows :*'
            5. Add fields for Idioms.

        else:
            Oops Embed :-
            1. Author Name = "Oops, Word couldn't be found :exclamation:"
            2. Footer Text = 'Requested by ' + context.message.author.nick
            3. Footer Icon Url = context.message.author.default_avatar_url
            4. Description = "\nI guess some words, even, Oxford, doesn't know. :see_no_evil: :joy:"
            5. Thumbnail = 'https://global.oup.com/academic/covers/pop-up/9780191836718'
        """

        embedstobereturned = []

        #If Word doesn't exist
        if not self.checkexistence():
            thisembed = Embed()
            thisembed.colour = Colour.red()
            thisembed.description = ":x: :exclamation:\n\nI guess some words, even Oxford, doesn't know. :laughing:"
            thisembed.set_thumbnail(url = "https://global.oup.com/academic/covers/pop-up/9780191836718")
            thisembed.set_author(name = "Oops, {} couldn't be found!".format(self.getname()))
            thisembed.set_footer(text = str("Requested by {} | Page 1".format(context.message.author.nick)), icon_url = context.message.author.avatar_url)

            #Embed ready!
            embedstobereturned.append(thisembed)

        #If Word exist
        else:
            #Working on the word
            self.generatesoup()
            self.fillparams()
            # self.displayeverything()

            #Working on the Embeds
            startembed = Embed()
            startembed.colour = Colour.blue()
            startembed.description = "Part of Speech = **{}**\nClick [here]({}) to go to the `Oxford 3000` page of *{}*".format(self.getpartofspeech(), self.geturl(), self.getname())
            if len(self.getmeanings()) == 0:
                startembed.description += "\n\n `Please Note:` {} doesn't have any **meanings** listed n the Oxford 3000 Webpage".format(self.getname())
            if len(self.getidioms()) == 0:
                startembed.description += "\n\n `Please Note:` {} doesn't have any **idoms** listed n the Oxford 3000 Webpage".format(self.getname())
            startembed.set_thumbnail(url = "https://global.oup.com/academic/covers/pop-up/9780191836718")
            startembed.set_footer(text = 'Requested by {} | Page {}'.format(context.message.author.nick, 1), icon_url = context.message.author.avatar_url)
            startembed.set_author(name = self.getname())

            if len(self.getphrasalverbs()) > 0:
                #Phrasal Verbs exist!
                pv = ""
                for thispv in self.getphrasalverbs():
                    pv += thispv + "\n"

                startembed.add_field(name = "Phrasal Verbs of {}".format(self.getname()), value = ("```\n{}\n\n```").format(pv), inline = False)
            if len(self.getsynonyms()) > 0:
                #Synonyms exist!
                syn = ""
                for thissyn in self.getsynonyms():
                    syn += thissyn + "\n"
                startembed.add_field(name = "Synonyms of {}".format(self.getname()), value = "```\n{}\n\n```".format(syn), inline = False)
            if len(self.getantonyms()) > 0:
                #Antonyms exist!
                ant = ""
                for thisant in self.getantonyms():
                    ant += thisant + "\n"
                startembed.add_field(name = "Antonyms of {}".format(self.getname()), value = "```\n{}\n\n```".format(ant), inline = False)
            if len(self.getnearbywords()) > 0:
                #Nearby Words exist!
                nw = ""
                for thisnw in self.getnearbywords():
                    nw += thisnw + "\n"
                startembed.add_field(name = "Nearby Words of {}".format(self.getname()), value = "```\n{}\n\n```".format(nw), inline = False)

            #Starting Embed Ready!
            embedstobereturned.append(startembed)

            #Check Meanings!
            if len(self.getmeanings()) > 0:
                meaningembed = Embed()
                meaningembed.colour = Colour.green()
                meaningembed.description = '*are as follows :*'
                meaningembed.set_footer(text = 'Requested by {} | Page {}'.format(context.message.author.nick, 2), icon_url = context.message.author.avatar_url)
                meaningembed.set_author(name = "Meanings for {}".format(self.getname()))

                c = 1
                for meaning in self.getmeanings():
                    meaningembed.add_field(name = "{}. {}".format(c, meaning['meaning']), value = (meaning['examples'].strip() if meaning['examples'] != '' else '*<No Examples>*'), inline = False)
                    c += 1

                #Meaning Embed Ready!
                if(c>1):
                    #It means there were meanings
                    embedstobereturned.append(meaningembed)

            #Check Idioms
            if len(self.getidioms()) > 0:
                #Yea, idioms exist.
                idiomembed = Embed()
                idiomembed.colour = Colour.orange()
                idiomembed.description = '*are as follows :*'
                idiomembed.set_footer(text = 'Requested by {} | Page {}'.format(context.message.author.nick, 3), icon_url = context.message.author.avatar_url)
                idiomembed.set_author(name = "Idioms for {}".format(self.getname()))

                c = 1
                for idiom in self.getidioms():
                    if(c==25):
                        #Already 25 idioms are added
                        break

                    idiomembed.add_field(name = "{}. {}".format(c, idiom['idiom']), value = "*means:* {}\n{}".format(idiom['meaning'].strip(), idiom['examples'].strip()), inline = False)
                    c += 1

                #Idiom Embed Ready!
                embedstobereturned.append(idiomembed)

                #Another Idiom Embed if there are many idioms
                if len(self.getidioms()) > 25:
                    #More idioms!
                    idiomembed = Embed()
                    idiomembed.colour = Colour.orange()
                    idiomembed.description = '*are as follows :*'
                    idiomembed.set_footer(text = 'Requested by {} | Page {}'.format(context.message.author.nick, 4), icon_url = context.message.author.avatar_url)
                    idiomembed.set_author(name = "Idioms for {}, Page 2".format(self.getname()))

                    c = 25
                    for idiom in self.getidioms()[24:]:
                        idiomembed.add_field(name = "{}. {}".format(c, idiom['idiom']), value = "*means:* {}\n{}".format(idiom['meaning'].strip(), idiom['examples'].strip()), inline = False)
                        c+=1

                    #Idiom Embed Ready!
                    embedstobereturned.append(idiomembed)

                    #Fingers crossed, must be max 50 idioms

        return embedstobereturned

    #Function to return the meaning in plain text:
    def return_plain_text_word_meaning(self):
        """It returns the word meaning in text format."""
        mean = ""
        #Word doesn't exist
        if not self.checkexistence():
            mean = "The word {} has no hit in Oxford 3000.".format(self.getname())
        #Word exits
        else:
            mean += "Word: " + "{}".format(self.getname()).upper()
            mean += "({})".format(self.getpartofspeech())
            mean += "\n"
            mean += "\nThe Oxford 3000 page is {}".format(self.geturl())
            mean += "\n"
            if len(self.getmeanings()) == 0:
                mean += "\n\nPlease Note: {} doesn't have any meanings listed in the Oxford 3000 Webpage".format(self.getname())
            else:
                mean += "\n\nMEANINGS :\n"
                c = 1
                for meaning in self.getmeanings():
                    mean += "\n{}. {} -\n{}\n".format(c, meaning['meaning'], meaning['examples'].strip() if meaning['examples'] != '' else '<No Examples>')
                    c += 1

            if len(self.getidioms()) == 0:
                mean += "\nPlease Note: {} doesn't have any idoms listed in the Oxford 3000 Webpage".format(self.getname())
            else:
                mean += "\n\nIDIOMS :\n"
                c=1
                for idiom in self.getidioms():
                    mean += "\n{}. {} -\nmeans:{}\n{}\n".format(c, idiom['idiom'], idiom['meaning'].strip(), idiom['examples'].strip())
                    c += 1

            if len(self.getphrasalverbs()) > 0:
                #Phrasal Verbs exist!
                pv = ""
                for thispv in self.getphrasalverbs():
                    pv += "> " + thispv + "\n"
                mean += "\n\nPHRASAL VERBS of {}:\n".format(self.getname()) + pv
            if len(self.getsynonyms()) > 0:
                #Synonyms exist!
                syn = ""
                for thissyn in self.getsynonyms():
                    syn += "> " + thissyn + "\n"
                mean += "\n\nSYNONYMS of {}:\n".format(self.getname()) + syn
            if len(self.getantonyms()) > 0:
                #Antonyms exist!
                ant = ""
                for thisant in self.getantonyms():
                    ant += "> " + thisant + "\n"
                mean += "\n\nANTONYMS of {}:\n".format(self.getname()) + ant
            if len(self.getnearbywords()) > 0:
                #Nearby Words exist!
                nw = ""
                for thisnw in self.getnearbywords():
                    nw += "> " + thisnw + "\n"
                mean += "\n\nNEARBY WORDS of {}:\n".format(self.getname()) + nw
        return mean

    #Main
    def main(self, word):
        self.setname(word)
        if (self.checkexistence()):
            #Exists
            self.generatesoup()
            self.fillparams()
            print(self.return_plain_text_word_meaning())
            # self.displayeverything()
        else:
            print(self.return_plain_text_word_meaning())

# # Test Call
# ob = Word()
# ob.main('life')
# del ob
