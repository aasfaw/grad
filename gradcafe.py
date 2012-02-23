from urllib import urlencode as uencode, urlopen as uopen
from BeautifulSoup import BeautifulSoup

subjects = [
                "Elec*",
                "EECE",
                "EE",
#                "Engineering",
                "EECS",
                "ECE"
]
schools = [
                "Caltech",
                "Harvard",
                "Michigan",
                "Stanford"
]
searchstring = "(" + "|".join(subjects) + ") (" + "|".join(schools) + ")"
gradcafe = "http://thegradcafe.com/survey/index.php?" + uencode({'q': searchstring}) + "&t=m&pp=250"

def getresult(result):
    
    if "dAccepted" in result:
        strreturn =  result[result.index("dAccepted") + 11:]
    elif "dRejected" in result:
        strreturn = result[result.index("dRejected") + 11:]
    elif "Other" in result:
        strreturn = result
    else:
        strreturn = ""
    
    if strreturn != "":
        gpa, GRE, GREsub,  = "", "", ""
        if "extinfo" in strreturn:
            gpas = strreturn.index("GPA</strong>:") + 14
            gpae = strreturn.index("<br/>", gpas)
            gpa = strreturn[gpas:gpae]
            GREs = strreturn.index("(V/Q/W)</strong>:") + 18
            GREe = strreturn.index("<br/>", GREs)
            GRE = strreturn[GREs:GREe]
            GREsubs = strreturn.index("Subject</strong>:") + 18
            GREsube = strreturn.index("<br/>", GREsubs)
            GREsub = strreturn[GREsubs:GREsube]

            strreturn = strreturn[:strreturn.index("extinfo")-11]

        strreturn = strreturn.replace("</span>","") + (" | " + gpa if gpa != "" else "")
        strreturn +=  ("/" + GRE if GRE != "" else "")
        strreturn +=  ("/" + GREsub if GREsub != "" else "")

    return strreturn

def fetchresults():
    page = uopen(gradcafe)
    soup = BeautifulSoup(page)
    import re
    for postrow in soup('tr', {'class':re.compile('row*')}):
        sn = str(postrow('td',{'class':'instcol'})[0].contents[0])
        m  = str(postrow('td')[1].contents[0])

        try:
            r  = str(postrow('td')[2]('span', {'class': re.compile('d*')})[0].contents[0]) + str(postrow('td')[2].contents[1])
        except:
            r  = str(postrow('td')[2].contents[0])

        d  = str(postrow('td',{'class':'datecol'})[0].contents[0])

        try:
            n  = str(postrow('ul',{'class':'control'})[0]('li')[1].contents[0])
        except: 
            n = ""

        yield " | ".join([sn, m, r, d, n])

def getlastresult():
    from os.path import exists
    if exists("gcsr"):
        return open("gcsr").read()
    else:
        return ""

def keepnotifying():
    from os.path import exists
    if exists("notify"):
        return bool(int(open("notify").read()))
    else:
        return False

def saveresult(strres):
    fhandle = open("gcsr",'w')
    fhandle.write(strres)
    fhandle.close()


def disablenotifications():
    fhandle = open("notify",'w')
    fhandle.write("0")
    fhandle.close()

def enablenotifications():
    fhandle = open("notify",'w')
    fhandle.write("1")
    fhandle.close()

def notify(ar, arraw):
    from os import system
    system("espeak -s 155 -a 200 " + ar  + " &")
    from easygui import msgbox
    msgbox(msg=arraw, title="New GradCafe Post", ok_button='OK')# == 'OK':
    #    disablenotifications()

def notifywrapper(resultstonotify):
    strspeak, strshow = "",""
    for resulttonotify in resultstonotify:
        if "Accepted" in resulttonotify: rawmsg = "Admission to " + resulttonotify.split("|")[0]
        elif "Rejected" in resulttonotify: rawmsg = "Rejection from " + resulttonotify.split("|")[0]
        elif "Wait listed" in resulttonotify: rawmsg = "Wait listed at " + resulttonotify.split("|")[0]
        else: continue
        modmsg = rawmsg.replace(" ", "\ ").replace("(","").replace(")","")
        strspeak += modmsg + "\ \ \ "
        strshow += rawmsg + "\n"
    
    notify(strspeak, strshow)
    

if __name__ == "__main__":

    from termcolor import colored
    resulttosave = ""
    lastresult = getlastresult()
    resultstonotify = []
    for result in fetchresults():
        if result != "":
            if resulttosave == "":
                resulttosave = result
            if result == lastresult:
                break
             
            resultstonotify.append(result)

    saveresult(resulttosave)
    
    # notify user if there's a new entry or if notifications are still enabled
    if len(resultstonotify) > 0 or keepnotifying():
        if len(resultstonotify) == 0:
            resultstonotify = [getlastresult()]
        enablenotifications()

        import sys
        if "-n" not in sys.argv:
            for result in resultstonotify: 
                print colored("-"*140,"blue")
                if "Accepted" in result: print colored(result, 'green')
                elif "Rejected" in result: print colored(result, 'red')
                else: print result
            notifywrapper(resultstonotify)
        else:
            disablenotifications()
