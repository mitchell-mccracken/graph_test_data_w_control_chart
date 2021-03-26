''' This program was made to create a control chart for test data. It was made to be scaled across multiple device platforms.
Select the desired date range (note must click 'store dates' prior to clicking 'graph data'). Then select the desired product test.
Then select the test step from the next drop down.

Note: This program does not have error handling when selecting test steps meaning errors will be generated if a non-number
step is chosen  '''

import fnmatch, os, datetime, pandas as pd, matplotlib.pyplot as mpl, PySimpleGUI as sg

''' --------------------------- delete old temp files ----------------- '''
os.chdir("C:/Temp/")
try:
    os.remove("temp_data_file.tsv")
except:
    pass
try:
    os.remove("temp_data_file2.tsv")
except:
    pass

''' ----------------- start with variables -------------------------- '''
s_date = 'test'
e_date = 'test'
layout1 = [[sg.Text('Test to get dates')],
            [sg.InputText('2020-05-20',key = '-start_date-')],
            [sg.CalendarButton('choose start date', target = '-start_date-', key='sdate')],
            [sg.InputText('2020-06-01', key='-end_date-')],
            [sg.CalendarButton('choose end date', target = '-end_date-', key='edate')],
            [sg.Button("store dates", key='Store_B'), sg.Button("graph data", key='-graph-')]]

window1 = sg.Window('test to get dates', layout1)

while True:  # Event Loop
    event, values = window1.read()
    if event in (None, 'Exit'):
        break
    if event == 'Store_B':
        StartDate, EndDate = values['-start_date-'], values['-end_date-']
        s_tuple = (StartDate[:4], StartDate[5:7], StartDate[8:10] )
        e_tuple = (EndDate[:4], EndDate[5:7], EndDate[8:10])
        # tuples are in yyyy[0] mm[1] dd[1] format
        print ('Start of date range:', s_tuple[0], s_tuple[1], s_tuple[2])
        print ('End of date range:', e_tuple[0], e_tuple[1], e_tuple[2])
    if event == '-graph-':
        break

window1.close()

s_date = datetime.date(int(s_tuple[0]), int(s_tuple[1]), int(s_tuple[2]))
og_s_date = s_date
e_date = datetime.date(int(e_tuple[0]), int(e_tuple[1]), int(e_tuple[2]))

delt = e_date - s_date
delta = delt.days
cur_date = str(s_date)
end_date = str(e_date)

today = str(datetime.date.today())
t_tuple = today.split("-")              #store today's date, need to avoid looking at current day's files which could cause an issue with the testers

''' -------------------set up files------------------------ '''
os.chdir("C:/Temp/")
f = open("temp_data_file.tsv", "a") #create temp file in temp folder, not sure if this is needed
f.close()

''' --------------- first window to select test --------- '''

directory = "//usdxysmrl1ms078/ptd$/POST_TEST_DATA/PostTestData/"
dir_list = os.listdir(directory)

layout2 = [[sg.Text('dropdown to select file folder')],
            [sg.Combo(dir_list, key='-tester-')],
            [sg.Button("Select Test Type", key='-test_type-')]]

window2 = sg.Window('dropdown test', layout2)

while True:
    event,values = window2.read()
    if event in (None, 'Exit'):
        break
    if event == '-test_type-':
        test_type = values['-tester-']
        break
window2.close()

new_dir = directory + test_type + "/"       #create a new directory for that test type
dir_list_tester = os.listdir(new_dir)       #create a list of all tester folder under that directory

os.chdir(new_dir)       # I don't think this is needed

''' ------ create a for loop to look for everything inside each tester folder ----'''

for x in dir_list_tester:
    new_dir_2 = new_dir + x +"/"
    if x[0] == '3':              #make sure folder is a teststation folder
        os.chdir(new_dir_2)
        while True:
            if  s_date > e_date:
                s_date = og_s_date
                break               #the issue is with this break is s_date is counted up and needs to be reset back to the orginal s_date to go through the loop again '''
            cur_date=str(s_date)
            with os.scandir() as listofentries:     #get all files from directory
                for entry in listofentries:
                    if entry.is_file():             #make sure entry is a file
                        file = str(entry)           #convert file to string, not sure if this is needed
                        year = str(cur_date)[:4]
                        month = str(cur_date)[5:7]
                        day = str(cur_date)[8:]
                        if file[11:15] == year and file[16:18] == month and file[19:21] == day: #filter based on matching year, month and day
                            file_loc = file[11:25]
                            with open(file_loc) as fp:
                                df=fp.read()                #store file contents as df so it can be written later

                            #print (file_loc)
                            os.chdir("C:/Temp/")
                            f=open("temp_data_file.tsv","a")    #open temp file to append for each loop
                            f.write(df)                         #append previously stored file contents to the temp file
                            f.close()                           #close temp file
                            os.chdir(new_dir_2)   #change back to original directory, this may not be needed


            #print (s_date)
            s_date += datetime.timedelta(days=1)

            f.close()

''' ------------------------------------------------------------------------------------------
    this section is to remove all header lines from the temp file so it is set up for graphing '''

os.chdir("C:/Temp/")
f = open("temp_data_file.tsv", "r") #create temp file in temp folder, not sure if this is needed
f2 = open("temp_data_file2.tsv","a")

header_line = f.readline()
num_columns = len(header_line.split('\t'))
f2.write(header_line)
print = len(header_line)

for x in f:
    line = x
    line_start = line[:6]       # only look at the first 6 characters of the line
    if line_start != "Serial" and len(line.split('\t')) == num_columns:  #ignore lines that are a header row and any lines that do not have the same number of columns as the header
        f2.write(line)

f.close()
f2.close()

''' -----------------------------------------------------
    this section is to create the data frame for graphing '''

test_param_list = ['']
columns = header_line.split('\t')
for x in columns:
    test_param_list.append(x)

layout3 = [[sg.Text('Select Test Parameter')],
            [sg.InputText('  ',key = '-t_param-')],
            [sg.Combo(test_param_list, key='-combo-')],
            [sg.Button('select', key='-select-')]]

window3 = sg.Window('Select Test Parameter', layout3)

while True:  # Event Loop
    event, values = window3.read()
    if event in (None, 'Exit'):
        break
    if event == '-select-':
        test_parameter = values['-combo-']
        window3['-t_param-'].update(test_parameter)
        break

window3.close()

y_label = test_parameter
os.chdir("C:/Temp/")
df = pd.read_csv("temp_data_file2.tsv", sep ='\t')
df.sort_values("Date", axis = 0, ascending =True, inplace = True, na_position ='last')
y_axis = pd.DataFrame(df, columns = [y_label])
len_y=len(y_axis)

#set up x axis list
x_axis = [0]
a=1
while a < len_y:
    x_axis.insert(1,a)
    a+=1
x_axis.sort()


''' ------------------ set up upper and lower spec limit ----------------- '''
usl=85
lsl=75

usl_y_axis = [usl]
a=1
while a< len_y:
    usl_y_axis.insert(1,usl)
    a+=1

lsl_y_axis = [lsl]
a=1
while a< len_y:
    lsl_y_axis.insert(1,lsl)
    a+=1

y_axis = y_axis.fillna(0)       #fill any non value with a 0
y_axis = y_axis.astype(float)   #change the text to float so it can be graphed

#print (x_axis)  #just to see the values
#print(y_axis)   #same as above

''' ---------------------------------- graph ------------------------------------ '''
#mpl.plot(x_axis,y_axis) #plot and show the plot
mpl.scatter(x_axis, y_axis, marker = '.')
mpl.plot(x_axis, usl_y_axis, color='red')       #graphs upper spec limit
mpl.plot(x_axis, lsl_y_axis, color='red')       #graphs lower spec limit
mpl.xlabel("count")
mpl.ylabel(test_parameter)
mpl.show()
