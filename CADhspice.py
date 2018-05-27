
###############################
import subprocess
import numpy as np
import shutil


#subprocess.call("date")

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()
print(" *** Running hspice InvChain.sp command ***\n", output)


#help(np.recfromcsv)
#help(np.genfromtxt)

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
print(Data["tphl_inv"])
tphl_prev = Data["tphl_inv"]

f = open('InvChain.sp', 'r')
f1 = open('InvChain1.sp','w')

#with open('InvChain.sp') as f:
#    read_data = f.read()

for line in f:
    if line == '.param fan = 1\n':
        line = '.param fan = 2\n'
#    print(line,end='')
    f1.write(line)


f.close()
f1.close()

shutil.copyfile('InvChain1.sp', 'InvChain.sp') 

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()
print(" *** Running hspice InvChain.sp command ***\n", output)

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
print(Data["tphl_inv"])
tphl_next = Data["tphl_inv"]

while tphl_next < tphl_prev:
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain1.sp','w')

    for line in f:
        if line == '.param fan = 8\n': #REVERSE
            line = '.param fan = 9\n'
        if line == '.param fan = 7\n': 
            line = '.param fan = 8\n'
        if line == '.param fan = 6\n': 
            line = '.param fan = 7\n'
        if line == '.param fan = 5\n': 
            line = '.param fan = 6\n'
        if line == '.param fan = 4\n': 
            line = '.param fan = 5\n'
        if line == '.param fan = 3\n': 
            line = '.param fan = 4\n'
        if line == '.param fan = 2\n': 
            line = '.param fan = 3\n'
        if line == '.param fan = 1\n': 
            line = '.param fan = 2\n'
        f1.write(line)


    f.close()
    f1.close()

    shutil.copyfile('InvChain1.sp', 'InvChain.sp') 

    p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()
    print(" *** Running hspice InvChain.sp command ***\n", output)

    Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
    print(Data["tphl_inv"])
    tphl_prev = tphl_next
    tphl_next = Data["tphl_inv"]
    