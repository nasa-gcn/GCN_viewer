from flask_backend import db
from flask_backend.models import Circular, Observatory, Event, Circular_body
from datetime import datetime
import numpy as np
import re
import os
import sys
import argparse

db.create_all()


class parseCircular():
    def __init__(self, i, evtList, verbose=False):
        self.parseData = {}
        self.parseData['id'] = 1
        self.parseData['sender'] = ''
        self.parseData['received'] = ''
        self.parseData['subject'] = ''
        self.parseData['body'] = ''
        self.parseData['event'] = ''
        self.parseData['evtid'] = 999999
        self.parseData['oid'] = 9999
        
        self._verbosity = verbose
        self.evtList = np.asarray(evtList)
        self._errF = False
        self._gcnNum = i
        self.__readCircular__()
        if not(self._errF):
            self.__findData__()
        
    
    def __readCircular__(self):
        if float(self._gcnNum) < 100:
            gcnN = '0{}'.format(self._gcnNum)
        else:
            gcnN = str(self._gcnNum)
        link = "./gcn3/{}.gcn3".format(gcnN)
        try:
            b = os.path.getsize(link)
            if b!=0:
                with open(link) as f:
                    gcn = [line.replace('\n','') for line in f.readlines()]
                self.gcn = gcn
            else:
                print("Circular {} is a wrong file".format(gcnN))
                self._errF = True
        except:
            print("Circular {} does not exist".format(gcnN))
            self._errF = True
        
    def __findData__(self):
        self._parseLine = [0, 0, 0, 0]
        for line, i in zip(self.gcn, range(len(self.gcn))):
            if line.find('NUMBER:') != -1 and self._parseLine[0]==0:
                self._parseLine[0] = i
            elif line.find('SUBJECT:') != -1 and self._parseLine[1]==0:
                self._parseLine[1] = i
            elif line.find('DATE:') != -1 and self._parseLine[2]==0:
                self._parseLine[2] = i
            elif line.find('FROM:') != -1 and self._parseLine[3]==0:
                self._parseLine[3] = i
    

    def parseCircular(self):
        if not(self._errF):
            self.__parseNumber__()
            self.__parseSubject__()
            self.__parseDate__()
            self.__parseEmail__()
            self.__parseEvent__()
            self.__parseObs__()
            self.__checkErr__()
            if not(self._errF):
                self.__parseBody__()
            if self._verbosity:
                if not(self._errF): print("Circular {}: Done".format(self._gcnNum))
                if self._verbosity == 2:
                    print(self.parseData)

    def __parseNumber__(self):
        j = self._parseLine[0]
        try:
            parsed = re.findall("NUMBER:\s+([0-9]+)", self.gcn[j])
            if np.size(parsed)>0:
                self.parseData['id'] = parsed[0]

        except:
            pass


    def __parseSubject__(self):
        j = self._parseLine[1]
        parsed = self.gcn[j][self.gcn[j].find(":")+1:]
        while parsed.find("  ") != -1:
            parsed= parsed.replace("  ", " ")
        if parsed[0] == ' ':
            parsed = parsed[1:]
        if np.size(parsed)>0:
            self.parseData['subject'] = parsed

    def __parseDate__(self):
        j = self._parseLine[2]
        try:
            parsed = re.findall("DATE:\s+([0-9]+)/([0-9]+)/([0-9]+)\s([0-9]+):([0-9]+):([0-9]+)", self.gcn[j])
            if np.size(parsed)>0:
                dt = parsed[0]
                if int(dt[0]) >90:
                    year = '19{}'.format(dt[0])
                else:
                    year = '20{}'.format(dt[0])
                self.parseData['received'] = datetime(int(year), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]))
        except:
            pass

    def __parseEvent__(self):
        
        subject = self.parseData['subject']

        tempC = ''
        for s in subject:
            if ord(s) > 1000:
                if self._verbosity:
                    print('\tThere is a special character, {}'.format(s))
            if ord(s) == 1057:
                tempC+='C'
            else:
                tempC+=s
        subject = tempC
        subject = subject.replace('"','')

        foundEvt = [evt for evt in self.evtList if evt[1] in subject]
        foundEvt += [evt for evt in self.evtList if (len(foundEvt) ==0) and evt[1].replace(" ", "") in subject]
        foundEvt += [evt for evt in self.evtList if (len(foundEvt) ==0) and evt[1].replace(" ", "-") in subject]
        foundEvt += [evt for evt in self.evtList if (len(foundEvt) ==0) and str(evt[2]) in subject]
        
        if len(foundEvt)==1:
            self.parseData['evtid'] = foundEvt[0][0]
            self.parseData['event'] = foundEvt[0][1]

    def __parseEmail__(self):
        j = self._parseLine[3]
        try:
            parsed = self.gcn[j][self.gcn[j].find("<")+1:self.gcn[j].find(">")]
            if np.size(parsed)>0:
                self.parseData['sender'] = parsed
        except:
            pass
    
    def __parseBody__(self):
        for line in self.gcn:
            self.parseData['body']+=line + "\n"

    def __parseObs__(self):
        ListOfObs = Observatory.query.all()

        title = " "+self.parseData['subject'][self.parseData['subject'].find(":")+1:]+" "

        title = title.replace("Fermi GRB", "GRB") # This is due to MASTER-NET reports
        title = title.replace(":", " ")
        title = title.replace("_", " ")
    
        ListOfTel = []

        for obs in ListOfObs:
            if obs.id < 1000:
                ListOfTel.append([obs.id, obs.telescope, obs.detector, obs.fullName])

        ListOfTel = np.asarray(ListOfTel)

        foundTel = [tel[0] for tel in ListOfTel if (title.find(" "+tel[1]+" ")>=0) or (title.find(" "+tel[1]+"/")>=0) or (title.find(" "+tel[1]+"-")>=0) or (title.find("("+tel[1]+")")>=0) or (title.find(" "+tel[1].upper()+" ")>=0)]
        foundTel += [tel[0] for tel in ListOfTel if (tel[0] not in foundTel) and ((tel[2]!=None) and (((title.find(" "+tel[2]+" ")>=0) or (title.find("("+tel[3]+")")>=0) or (title.find(" "+tel[3].upper()+" ")>=0))))]
        foundTel += [tel[0] for tel in ListOfTel if (tel[0] not in foundTel) and (((title.find(" "+tel[3]+" ")>=0) or (title.find(" "+tel[3]+"/")>=0) or (title.find(" "+tel[3]+"-")>=0) or (title.find("("+tel[3]+")")>=0) or (title.find(" "+tel[3].upper()+" ")>=0)))]
        foundTel += [tel[0] for tel in ListOfTel if (tel[0] not in foundTel) and (np.size(foundTel) == 0) and ((tel[1] == 'LIGO/Virgo' or tel[1] == 'IceCube' or tel[1] == 'ANTARES') and (self.parseData['subject'].find(tel[1])>=0))]

        if np.size(foundTel)== 1:
            foundObs = ListOfTel[ListOfTel[:,0]==foundTel[0]]
            self.parseData['oid'] = foundObs[0][0]

        elif np.size(foundTel)== 0:
            if (title.find(' radio ') >=0) or (title.find(' Radio ') >=0):
                self.parseData['oid'] = 1001
            elif (title.find(' optical ') >=0) or (title.find(' optical/') >=0) or (title.find(' Optical ') >=0) or (title.find(' near-IR ') >=0) or (title.find(' IR ') >=0) or (title.find(' infrared ') >=0)  or (title.find(' Infra-Red ') >=0) :
                self.parseData['oid'] = 1002
            elif (title.find(' X-ray ') >=0):
                self.parseData['oid'] = 1003

        else:
            foundObs = np.asarray([obs for obs in ListOfTel if obs[0] in foundTel])
            if len(set(foundObs[:,1]))==1:
                foundObs = ListOfTel[ListOfTel[:,1]==foundObs[0][1]]
                foundDtr = []
                for dtr in foundObs[foundObs[:,2]!=None]:
                    if title.find(dtr[2])>=0:
                        foundDtr.append(dtr[2])

                if len(foundDtr) == 1:
                    self.parseData['oid'] = foundObs[foundObs[:,2]==foundDtr][0][0]
                else:
                    self.parseData['oid'] = foundObs[foundObs[:,2]==None][0][0]
                        
    def __checkErr__(self):
        if 0 in self._parseLine:
            print('Error in parsing data, Circular {}'.format(self._gcnNum))
            self._errF=True
        elif self.parseData['event'] == "":
            print('Event name is not found in Circular {}'.format(self._gcnNum))

        
    def gendb(self):
        return Circular(self.parseData['id'], self.parseData['sender'], self.parseData['received'], 
            self.parseData['subject'], self.parseData['oid'], self.parseData['evtid'], self.parseData['id'])

    def gendb_body(self):
        return Circular_body(self.parseData['id'], self.parseData['body'])


if __name__ == "__main__":
    old_stdout = sys.stdout

    parser = argparse.ArgumentParser()
    parser.add_argument("-start", type=int, default = 31, help="Start number")
    parser.add_argument("-end",type=int, default=27354, help="End number")
    parser.add_argument("-v", type=bool, default=False, help="Verbosity")

    args = parser.parse_args()
    
    with open("./backfill.log","w") as log_file:

        sys.stdout = log_file
        j = 1

        evts = Event.query.all()

        evtList = []
        for evt in evts:
            event = evt.event.replace("IC ", "IceCube ")
            eevent = evt.event.replace("A ", "ANTARES ")
            if len(evt.notices) == 0:
                evtList.append([evt.id, event, None])
            else:
                for en in  evt.notices:
                    evtList.append([evt.id, event, en.tid])

        for i in range(args.start, args.end+1):
            p = parseCircular(i, evtList, verbose=args.v)
            p.parseCircular()
            if not(p._errF):
                db.session.add(p.gendb())
                db.session.add(p.gendb_body())
                j+=1
                db.session.commit()

    sys.stdout = old_stdout
    
