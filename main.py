################################################################################################################################
import subprocess
import numpy as np
import shutil
import re

mintphl=[] #All Stage minimum Delays are stored in this array
###################################################################################################################################### EDIT InvChain.sp
f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    if line == ('.measure TRAN tphl_inv  TRIG v(Xinv1.a) VAL = 1.5 RISE = 1 TARG v(Xinv5.z) VAL=1.5 FALL = 1\n'):
        line = '.measure TRAN tphl_inv  TRIG v(Xinv1.a) VAL = 1.5 RISE = 1 TARG v(z) VAL=1.5 FALL = 1\n'
    f1.write(line)
f.close()
f1.close()

shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

###################################################################################################################################### STAGE 1

f = open('InvChain.sp', 'r') #opens readable InvChain.sp
f1 = open('InvChain3.sp','w') #opens writable InvChain.sp
tphl=[]
stage = 1

############ 
## code to kickoff the sweep .param fan (basically .param fan = 1 to .param fan = 2)

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE) #Contacts Hspice with PIPE method
output,err = p.communicate() #Saves to output

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3) #creates a .csv that stores delay value
tphl.append(Data["tphl_inv"]) #the delay value is appended to a list called tphl(different for every block) 
tphl_prev = Data["tphl_inv"] 

for line in f:
    if line == '.param fan = 1\n':
        line = '.param fan = 2\n'
    f1.write(line)
f.close()
f1.close()

shutil.copyfile('InvChain3.sp', 'InvChain.sp') #copies the newly written InvChain3.sp to InvChain.sp

############ 
## code to sweep .param fan

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)#Contacts Hspice with PIPE metho
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl.append(Data["tphl_inv"])
tphl_next = Data["tphl_inv"]

while tphl_next < tphl_prev: #this loop is used for sweeping the fan values uptil the previous delay is greater than the next
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

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
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

    p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()

    Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
    tphl.append(Data["tphl_inv"])
    tphl_prev = tphl_next
    tphl_next = Data["tphl_inv"]
print('List of delays for stage 1: ',tphl) #displays the created list called tphl
print('Minimum tphl: ',min(tphl)) #displays the minimum tphl from the list
Fanoutmin = tphl.index(min(tphl)) + 1 #Prints out Index of the minimum delay and add1 since indexes start from 0 (for fanout)
print ('Fanout- For minimum tphl: ', Fanoutmin)
print("Maximum tphl: ",max(tphl)) #displays the minimum tphl from the list (not needed)
Fanoutmax = tphl.index(max(tphl)) + 1 #Prints out Index of the minimum delay and add1 since indexes start from 0 (for fanout) (not needed
print ('Fanout- For maximum tphl: ', Fanoutmax)
print('Number of stages (Inverters): ',stage)
mintphl.append(min(tphl)) #appends minimum delay to a list called mintphl

############ 
## Code to change line to .param fan = 1 for reloop

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    match = re.search(r'(param\sfan\s=\s)(\d)',line) #using regex, the fan value is brought back to 1 to process Hspice for the next stage.
    if match: 
        numbertxt = match.group(2)
        newnumber = 1
        newnumbertxt = str(newnumber)
        line = re.sub(r'\d',newnumbertxt,line)
        f1.write(line)
    else:
        f1.write(line)
f.close()
f1.close()

shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

###################################################################################################################################### STAGE 3

stage = 3
tphl3=[]

############ 
## code to create 3 stages (Inverters)

if stage == 3 : 
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

    for line in f: #this part of the code is used to create the several stages 3,5
        match = re.search(r'^X',line)
        if match: 
            f1.write('')
        else:
            f1.write(line)
        match = re.search(r'Cload', line)
        if match:
            line = 'Xinv1 a 2 inv M='+str(1)+'\n'
            f1.write(line)
            for j in np.arange(1,stage-1,1):
                line = 'Xinv'+str(j+1)+' '+str(j+1)+' '+str(j+2)+' inv M='+str('fan**{0}'.format(j))+'\n'
                f1.write(line)
            line = 'Xinv'+str(j+2)+' '+str(stage)+' z inv M='+str('fan**{0}'.format(stage-1))+'\n'
            f1.write(line)
    f.close()
    f1.close()
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to kickoff the sweep .param fan (basically .param fan = 1 to .param fan = 2)

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl3.append(Data["tphl_inv"])
tphl_prev = Data["tphl_inv"]

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    if line == '.param fan = 1\n':
        line = '.param fan = 2\n'
    f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to sweep .param fan

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl3.append(Data["tphl_inv"])
tphl_next = Data["tphl_inv"]

while tphl_next < tphl_prev:
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

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
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

    p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()

    Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
    tphl3.append(Data["tphl_inv"])
    tphl_prev = tphl_next
    tphl_next = Data["tphl_inv"]
print('List of delays for stage 3: ',tphl3)
print('Minimum tphl: ',min(tphl3))
Fanoutmin = tphl3.index(min(tphl3)) + 1 
print ('Fanout- For minimum tphl: ', Fanoutmin)
print("Maximum tphl: ",max(tphl3))
Fanoutmax = tphl3.index(max(tphl3)) + 1
print('Fanout- For maximum tphl: ',Fanoutmax)
print('Number of stages (Inverters): ',stage)
mintphl.append(min(tphl3))
############
## Code to change line to .param fan = 1 for reloop

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    match = re.search(r'(param\sfan\s=\s)(\d)',line)
    if match: 
        numbertxt = match.group(2)
        newnumber = 1
        newnumbertxt = str(newnumber)
        line = re.sub(r'\d',newnumbertxt,line)
        f1.write(line)
    else:
        f1.write(line)
f.close()
f1.close()

shutil.copyfile('InvChain3.sp', 'InvChain.sp')  

###################################################################################################################################### STAGE 5

stage = 5
tphl5=[]

############ 
## code to create 5 stages (Inverters)

if stage == 5 :
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

    for line in f:
        match = re.search(r'^X',line)
        if match: 
            f1.write('')
        else:
            f1.write(line)
        match = re.search(r'Cload', line)
        if match:
            line = 'Xinv1 a 2 inv M='+str(1)+'\n'
            f1.write(line)
            for j in np.arange(1,stage-1,1):
                line = 'Xinv'+str(j+1)+' '+str(j+1)+' '+str(j+2)+' inv M='+str('fan**{0}'.format(j))+'\n'
                f1.write(line)
            line = 'Xinv'+str(j+2)+' '+str(stage)+' z inv M='+str('fan**{0}'.format(stage-1))+'\n'
            f1.write(line)
    f.close()
    f1.close()
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to kickoff the sweep .param fan (basically .param fan = 1 to .param fan = 2)

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl5.append(Data["tphl_inv"])
tphl_prev = Data["tphl_inv"]

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    if line == '.param fan = 1\n':
        line = '.param fan = 2\n'
    f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to sweep .param fan

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl5.append(Data["tphl_inv"])
tphl_next = Data["tphl_inv"]

while tphl_next < tphl_prev:
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

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
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

    p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()

    Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
    tphl5.append(Data["tphl_inv"])
    tphl_prev = tphl_next
    tphl_next = Data["tphl_inv"]
print('List of delays for stage 5: ',tphl5)
print('Minimum tphl: ',min(tphl5))
Fanoutmin = tphl5.index(min(tphl5)) + 1 
print ('Fanout- For minimum tphl: ', Fanoutmin)
print("Maximum tphl: ",max(tphl5))
Fanoutmax = tphl5.index(max(tphl5)) + 1
print ('Fanout- For maximum tphl: ', Fanoutmax)
print ('Number of stages (Inverters): ',stage)
mintphl.append(min(tphl5))
############
## Code to change line to .param fan = 1 for reloop

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    match = re.search(r'(param\sfan\s=\s)(\d)',line)
    if match: 
        numbertxt = match.group(2)
        newnumber = 1
        newnumbertxt = str(newnumber)
        line = re.sub(r'\d',newnumbertxt,line)
        f1.write(line)
    else:
        f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp')  

###################################################################################################################################### STAGE 7

stage = 7
tphl7=[]

############ 
## code to create 5 stages (Inverters)

if stage == 7 :
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

    for line in f:
        match = re.search(r'^X',line)
        if match: 
            f1.write('')
        else:
            f1.write(line)
        match = re.search(r'Cload', line)
        if match:
            line = 'Xinv1 a 2 inv M='+str(1)+'\n'
            f1.write(line)
            for j in np.arange(1,stage-1,1):
                line = 'Xinv'+str(j+1)+' '+str(j+1)+' '+str(j+2)+' inv M='+str('fan**{0}'.format(j))+'\n'
                f1.write(line)
            line = 'Xinv'+str(j+2)+' '+str(stage)+' z inv M='+str('fan**{0}'.format(stage-1))+'\n'
            f1.write(line)
    f.close()
    f1.close()
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to kickoff the sweep .param fan (basically .param fan = 1 to .param fan = 2)

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl7.append(Data["tphl_inv"])
tphl_prev = Data["tphl_inv"]

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    if line == '.param fan = 1\n':
        line = '.param fan = 2\n'
    f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to sweep .param fan

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl7.append(Data["tphl_inv"])
tphl_next = Data["tphl_inv"]

while tphl_next < tphl_prev:
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

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
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

    p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()

    Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
    tphl7.append(Data["tphl_inv"])
    tphl_prev = tphl_next
    tphl_next = Data["tphl_inv"]
print('List of delays for stage 5: ',tphl7)
print('Minimum tphl: ',min(tphl7))
Fanoutmin = tphl7.index(min(tphl7)) + 1
print ('Fanout- For minimum tphl: ', Fanoutmin)
print("Maximum tphl: ",max(tphl7))
Fanoutmax = tphl7.index(max(tphl7)) + 1
print ('Fanout- For maximum tphl: ', Fanoutmax)
print ('Number of stages (Inverters): ',stage)
mintphl.append(min(tphl7))
############
## Code to change line to .param fan = 1 for reloop

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    match = re.search(r'(param\sfan\s=\s)(\d)',line)
    if match: 
        numbertxt = match.group(2)
        newnumber = 1
        newnumbertxt = str(newnumber)
        line = re.sub(r'\d',newnumbertxt,line)
        f1.write(line)
    else:
        f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp')  

###################################################################################################################################### STAGE 9

stage = 9
tphl9=[]

############ 
## code to create 5 stages (Inverters)

if stage == 9 :
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

    for line in f:
        match = re.search(r'^X',line)
        if match: 
            f1.write('')
        else:
            f1.write(line)
        match = re.search(r'Cload', line)
        if match:
            line = 'Xinv1 a 2 inv M='+str(1)+'\n'
            f1.write(line)
            for j in np.arange(1,stage-1,1):
                line = 'Xinv'+str(j+1)+' '+str(j+1)+' '+str(j+2)+' inv M='+str('fan**{0}'.format(j))+'\n'
                f1.write(line)
            line = 'Xinv'+str(j+2)+' '+str(stage)+' z inv M='+str('fan**{0}'.format(stage-1))+'\n'
            f1.write(line)
    f.close()
    f1.close()
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to kickoff the sweep .param fan (basically .param fan = 1 to .param fan = 2)

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl9.append(Data["tphl_inv"])
tphl_prev = Data["tphl_inv"]

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    if line == '.param fan = 1\n':
        line = '.param fan = 2\n'
    f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

############ 
## code to sweep .param fan

p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
output,err = p.communicate()

Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
tphl9.append(Data["tphl_inv"])
tphl_next = Data["tphl_inv"]

while tphl_next < tphl_prev:
    f = open('InvChain.sp', 'r')
    f1 = open('InvChain3.sp','w')

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
    shutil.copyfile('InvChain3.sp', 'InvChain.sp') 

    p=subprocess.Popen(["hspice","InvChain.sp"], stdout=subprocess.PIPE)
    output,err = p.communicate()

    Data = np.recfromcsv("InvChain.mt0.csv",comments="$",skip_header=3)
    tphl9.append(Data["tphl_inv"])
    tphl_prev = tphl_next
    tphl_next = Data["tphl_inv"]
print('List of delays for stage 5: ',tphl9)
print('Minimum tphl: ',min(tphl9))
Fanoutmin = tphl9.index(min(tphl9)) + 1
print ('Fanout- For minimum tphl: ', Fanoutmin)
print("Maximum tphl: ",max(tphl9))
Fanoutmax = tphl9.index(max(tphl9)) + 1
print ('Fanout- For maximum tphl: ', Fanoutmax)
print ('Number of stages (Inverters): ',stage)
mintphl.append(min(tphl9))

############
## Code to change line to .param fan = 1 for reloop

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    match = re.search(r'(param\sfan\s=\s)(\d)',line)
    if match: 
        numbertxt = match.group(2)
        newnumber = 1
        newnumbertxt = str(newnumber)
        line = re.sub(r'\d',newnumbertxt,line)
        f1.write(line)
    else:
        f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp')  
###################################################################################################################################### Making Netlist (Final Step)

print ('\nMinimum Delays for each stage(1,3,5,7,9): ',mintphl)
print ('Overall Minimum Delay', min(mintphl))
print (mintphl.index(min(mintphl)))

if (mintphl.index(min(mintphl))== 0):
    stage = 1
elif (mintphl.index(min(mintphl))== 1):
    stage = 3
elif (mintphl.index(min(mintphl))== 2):
    stage = 5
elif (mintphl.index(min(mintphl))== 3):
    stage = 7
elif (mintphl.index(min(mintphl))== 4):
    stage = 9

print ('Stage with minimum Delay: ', stage)
print ('New Netlist Created: InvChain.sp')

f = open('InvChain.sp', 'r')
f1 = open('InvChain3.sp','w')

for line in f:
    match = re.search(r'^X',line)
    if match: 
        f1.write('')
    else:
        f1.write(line)
    match = re.search(r'Cload', line)
    if match:
        line = 'Xinv1 a 2 inv M='+str(1)+'\n'
        f1.write(line)
        for j in np.arange(1,stage-1,1):
            line = 'Xinv'+str(j+1)+' '+str(j+1)+' '+str(j+2)+' inv M='+str('fan**{0}'.format(j))+'\n'
            f1.write(line)
        line = 'Xinv'+str(j+2)+' '+str(stage)+' z inv M='+str('fan**{0}'.format(stage-1))+'\n'
        f1.write(line)
f.close()
f1.close()
shutil.copyfile('InvChain3.sp', 'InvChain.sp') 


###################################################################################################################################### Final Answer
## Since Stage 5 has the lowest delay of 5.7880000000000001e-10, 5 inverters are the optimal solution. The new netlist formed contains 5 Inverters with M starting from 1 to Fan**4.



