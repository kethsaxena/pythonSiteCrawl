import os 
import datetime as dt
import re 


base="/fledging/projects/min_hdl/output"
projPath=base+"/"+dt.datetime.today().strftime('%B')
try:
    os.chdir(projPath)
except:
    os.mkdir(projPath)
    os.chdir(projPath)

#print(projPath)

fName="{:%Y%m%d}".format(dt.datetime.today())


try:        
    if not os.path.isdir(fName):
        os.mkdir(fName)
        os.chdir(projPath+"/"+fName)
    else:
        os.chdir(projPath+"/"+fName)
        pass

    dir_list = next(os.walk('.'))[1]
    actualList=[item for item in dir_list if re.match("^run",item)]
    actualList.sort()
    folNum=int(actualList[len(actualList)-1].split("run")[1])+1
    os.mkdir("run"+str(folNum))
except IndexError:
    os.mkdir("run"+str(1))

print(fName+" Created")

