from flask_backend import db
from flask_backend.models import Event
import numpy as np
import re
import os
import sys
import argparse

db.create_all()


class parseCircular():
    def __init__(self, i, j, verbose=False):
        self.parseData = {}
        
        self.parseData['event'] = ''
        self.parseData['evttype'] = ''
        
        self._verbosity = verbose
        self._errF = False
        self._gcnNum = i
        self._idx = j
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
        self._parseLine = 0
        for line, i in zip(self.gcn, range(len(self.gcn))):
            if line.find('SUBJECT:') != -1 and self._parseLine==0:
                self._parseLine = i
                break

    def __parseSubject__(self):
        j = self._parseLine
        parsed = self.gcn[j][self.gcn[j].find(":")+1:]
        while parsed.find("  ") != -1:
            parsed= parsed.replace("  ", " ")
        if parsed[0] == ' ':
            parsed = parsed[1:]
        if np.size(parsed)>0:
            self.parseData['subject'] = parsed

    def parseCircular(self):
        if not(self._errF):
            self.__parseSubject__()
            self.__parseEvent__()
            self.__checkErr__()
            if self._verbosity:
                if not(self._errF): print("Circular {}: Done".format(self._gcnNum))
                if self._verbosity == 2:
                    print(self.parseData)


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

        try:
            tempE = re.findall("(GRB|G|S|IceCube|ANTARES|GW|grb)[-|\s]?([0-9])([0-9])([0-9])([0-9])([0-9])([0-9])([A-Ea-z]+)", subject)[0]
            
        except:
            try:
                tempE = re.findall("(GRB|G|S|IceCube|ANTARES|GW|grb)[-|\s]?([0-9])([0-9])([0-9])([0-9])([0-9])([0-9])\.([0-9]+)", subject)[0]
                tempE[-1] = ''
                
            except:
                try:
                    tempE = re.findall("(GRB|G|S|IceCube|LIGO/Virgo|ANTARES|GW|grb)[-|\s]?([0-9])([0-9])([0-9])([0-9])([0-9])([0-9])()", subject)[0]
                    
                except:
                    tempE = ('', '', '', '', '', '', '', '')
                    pass

        # Define the event name
        if (tempE[0] == "IceCube") or (tempE[0] == "IceCube Alert"):
            self.parseData['event'] = "IC {}{}{}{}{}{}{}".format(*tempE[1:])
            self.parseData['evttype'] = "\u03BD"
        elif (tempE[0] == "ANTARES") or (tempE[0] == "ANTARES alert"):
            self.parseData['event'] = "A {}{}{}{}{}{}{}".format(*tempE[1:])
            self.parseData['evttype'] = "\u03BD"
        elif tempE[0] == 'S' or tempE[0] == 'G' :
            self.parseData['event'] = "{} {}{}{}{}{}{}{}".format(*tempE)
            self.parseData['evttype'] = "GW"
        elif tempE[0] == 'LIGO/Virgo':
            self.parseData['event'] = "S {}{}{}{}{}{}{}".format(*tempE[1:])
            self.parseData['evttype'] = "GW"
        elif tempE[0] == 'GRB':
            self.parseData['event'] = "GRB {}{}{}{}{}{}{}".format(*tempE[1:])
            self.parseData['evttype'] = "GRB"
        else:
            self.parseData['event'] = ""
            self.parseData['evttype'] = "others"

        
    def __checkErr__(self):
        if self._parseLine==0:
            print('Error in parsing data, Circular {}'.format(self._gcnNum))
            self._errF=True
        elif self.parseData['event'] == "":
            print('Event name is not found in Circular {}'.format(self._gcnNum))

        
    def gendb(self, j):
        return Event(j, self.parseData['event'],  self.parseData['evttype'], None, None, None, None, None, None)


if __name__ == "__main__":
    old_stdout = sys.stdout

    parser = argparse.ArgumentParser()
    parser.add_argument("-start", type=int, default = 31, help="Start number")
    parser.add_argument("-end",type=int, default=27354, help="End number")
    parser.add_argument("-v", type=bool, default=False, help="Verbosity")

    args = parser.parse_args()
    evtList = {}
    
    with open("./backfill_evt.log","w") as log_file:

        sys.stdout = log_file
        j=1
        GW_j = 100001
        nu_j = 200001
        for i in range(args.start, args.end+1):
            p = parseCircular(i, j, verbose=args.v)
            p.parseCircular()
            if not(p._errF) and p.parseData['evttype'] !='others' and p.parseData['evttype'] !='GRB':
                if p.parseData['event'] not in evtList.keys():
                    if p.parseData['evttype'] == 'GW':
                        db.session.add(p.gendb(GW_j))
                        GW_j+=1
                        db.session.commit()
                    else:
                        db.session.add(p.gendb(nu_j))
                        nu_j+=1
                        db.session.commit()
                    evtList[p.parseData['event']] = 1
                    j+=1


    sys.stdout = old_stdout
    
