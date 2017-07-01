# -*- coding: utf-8 -*-
"""
kay - automated data migration bot 

kay will automate the process of inputing data from an existing 
tsv (tab separated values) file into a web form (which a web service 
would further process the data). It accomplishes this by using
pyautogui to move the mouse and type in the form. After focus is 
obtained, the '\t' character is used to navigate the page.
File selection is done manually.

kay also supports unicode characters. kay uses pyperclip in order
to achieve this.

kay currently work only on Windows. kay is not guaranteed to 
work on Mac and Linux.

Confidential elements are marked with 'xxx'.

Created on Wed Jun 28 14:38:00 2017

@author: Kris
"""
import pyautogui
import pyperclip
import time
import csv
import sys

#### CONFIG ####
DEFAULT_POS_DELAY_SEC = 3
FILEPATH   = r"xxx"
#[new, display, property] click positions are at full scroll up
CLICK_BLANK = (0.97, 0.94)
CLICK_NEW = (0.518, 0.420)
CLICK_DISPLAY = (0.52, 0.50)
CLICK_PROPERTY = (0.566, 0.435)

#### UTIL METHODS ####
def pos(delay = DEFAULT_POS_DELAY_SEC):
    time.sleep(delay)
    p = pyautogui.position()
    print("(" + ('%.5f' % (p[0]/width)) + "," + ('%.5f' % (p[1]/height)) + ")")
    
def type_unicode(word):
    pyperclip.copy(word)
    pyautogui.hotkey("ctrl", "v")

width, height = pyautogui.size()

#### CLICK METHODS ####

def clickBlankArea():
    #(1) Any blank area in website (doesn't do anything on click -- only focus)
    pyautogui.click(width * CLICK_BLANK[0], height * CLICK_BLANK[1])

def clickNewButton():
    #(2)'New' button
    clickBlankArea()
    pyautogui.scroll(3000)
    time.sleep(0.1)
    pyautogui.click(width * CLICK_NEW[0], height * CLICK_NEW[1])

def clickDisplayBox():
    #(3)'Display title' input text box
    clickBlankArea()
    pyautogui.scroll(3000)
    time.sleep(0.1)
    pyautogui.click(width * CLICK_DISPLAY[0], height * CLICK_DISPLAY[1])

def clickPropertyTab():
    #(4)'Property' tab
    clickBlankArea()
    pyautogui.scroll(3000)
    time.sleep(0.1)
    pyautogui.click(width * CLICK_PROPERTY[0], height * CLICK_PROPERTY[1])

#### WORKFLOW METHODS ####
    
# Clicks the New content sequence in the 'xxx' Page 
def clickNewContent():
    clickNewButton()    
    time.sleep(0.1)

    #'xxx' Button
    pyautogui.press('enter')

    #'xxx' Button
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('enter')

# Clicks any where in the 'xxx' text input field and fills in form 
last_date_str = ""
repeat_count = 0
def typeNewContent(line_index, display, desc, id, date_str, title, filename):
    global last_date_str
    global repeat_count
    
    # need to maintain ordering after sort by date -- do this by changing time
    if (date_str == ""):
        print("[ERROR]:: date_str is empty!")
        return None
    elif (date_str == last_date_str):
        repeat_count = repeat_count + 1
        if (repeat_count >= 59):
            print("[ERROR]:: repeat_count is more than 59
            return None
    else:
        last_date_str = date_str
        repeat_count = 0

    time_str = "12:00:" + str(repeat_count).zfill(2) + " AM"
    
    clickDisplayBox()
    time.sleep(0.1)
    type_unicode(display)
    pyautogui.typewrite("\t\t")
    type_unicode(desc)
    pyautogui.typewrite("\t\t\t\t")
    type_unicode(id)
    pyautogui.typewrite("\t\t")
    type_unicode(date_str)
    pyautogui.typewrite("\t")
    type_unicode(time_str)
    pyautogui.typewrite("\t\t\t")
    type_unicode(title)
    pyautogui.typewrite("\t\t\t\t")
    pyautogui.typewrite("\n")

    time.sleep(0.1)
    response = pyautogui.alert('(1) Press OK When file is selected\nindex=' + line_index + ', filename = ' + filename)
    if (response is None):
        print("user-requested exit")
        sys.exit()

    clickBlankArea()
    pyautogui.scroll(3000)

    return time_str


def propertyClick(date_str = "test_date", time_str = "test_time"):
    clickPropertyTab()
    time.sleep(3.0)

    # xxx Tab
    pyautogui.typewrite("\t\t\t\t\t\t\t\t\t\t\t\n")
    
    pyautogui.typewrite("\t\t\t\t\t\t")
    pyautogui.typewrite(date_str)
    pyautogui.typewrite("\t")
    pyautogui.typewrite(time_str)
    pyautogui.typewrite("\n\t")
    clickBlankArea()
    time.sleep(0.1)
    pyautogui.scroll(1000)
    time.sleep(0.1)


#### MAIN METHOD ####
def run(fIndex, tIndex):
    with open(FILEPATH, encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        i = 0
        for row in reader:
            if (i < fIndex):  # +1 header, -1 (first_index = 1)
                i = i + 1
                continue
            if (i > tIndex):  # +1 header, -1 (first_index = 1)
                break
            else:
                index = row[0]
                id = row[1]
                date_str = row[2]
                title = row[3]
                filename = row[4]
                print(row)
                if (index == "" or booknum == "" or date_str == "" or title == ""):
                    pyautogui.alert('Unable to process: field(s) are blank. please complete and publish manually... index=' + index + ", id=" + id)
                    response = pyautogui.confirm("(2) Check details, then go back to 'xxx' Page and press OK. Press Cancel to stop operation.")
                    if (response is 'Cancel' or response is None):
                        print("user-requested exit")
                        break
                    i = i + 1
                    continue
                clickNewContent()
                time.sleep(1.0)
                get_time_str = typeNewContent(index, title, title, id, date_str, title, filename)
                if (get_time_str is None):
                    pyautogui.alert('Unable to process: time_str overflow. please complete and publish manually...')
                    response = pyautogui.confirm("(2) Check details, then go back to 'xxx' Page and press OK. Press Cancel to stop operation.")
                    if (response is 'Cancel' or response is None):
                        print("user-requested exit")
                        break
                    i = i + 1
                    continue
                time.sleep(0.5)
                propertyClick(date_str, get_time_str)
                pyautogui.moveTo(0.5 * width, 0.5 * height) 
                response = pyautogui.confirm("(2) Check details, then go back to 'xxx' Page and press OK. Press Cancel to stop operation.")
                if (response is 'Cancel' or response is None):
                    print("user-requested exit")
                    break
                i = i + 1

        pyautogui.alert("FINISHED")


#### SCRIPT ####

print("================ Automation script ===============")
print("type 'run(<from>, <to>)' to run automation script")
print("    <from> and <to> is inclusive and required:")
print("    run(306, 310) will run 5 records")
print("type 'pos(<delay>)' to get position of cursor")
print("    <delay> is in seconds and is optional")
print("    default <delay> is 3 seconds")
print("don't forget to set 'filepath' and 4 clicking")
print("    positions: [BLANK, NEW, DISPLAY, PROPERTY]")

