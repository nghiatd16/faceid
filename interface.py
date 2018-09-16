from tkinter import *
import _thread
import time
import vision_config
import logging
from interact_database_v2 import Database
from object_DL import Person
STATUS_INACTIVE = 0
STATUS_INPROGRESS = 1
STATUS_DONE = 2
STATUS = STATUS_INACTIVE
STATUS_CONFIRM = 3
result = None
msg_result = None

# db = Database(vision_config.DB_HOST, vision_config.DB_USER, vision_config.DB_PASSWD, vision_config.DB_NAME)
db = None
def response_idCode_OK(idCode):
    person = db.getPersonByIdCode(idCode)
    if person is None:
        get_information(idCode)
    else:
        show_information(vision_config.TRANSFER_LEARNING_MSG, person)
    # STATUS = STATUS_DONE

def response_learning_OK(msg, person):
    global STATUS, result, msg_result
    logging.info("{} | person [id: {} - name: {} - idCode: {} - age: {} - gender: {}]".format(msg, \
                                                                    person.id, person.name, person.idcode, person.age, person.gender))
    result = person
    msg_result = msg
    STATUS = STATUS_DONE

def response_cancel():
    global STATUS
    STATUS = STATUS_INACTIVE
    result = None

def reset():
    global STATUS
    STATUS = STATUS_INACTIVE
    result = None

def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def show_information(msg, person):
    name = person.name
    idCode = person.idcode
    age = person.age
    gender = person.gender

    global STATUS
    STATUS = STATUS_CONFIRM
    label = None
    root = Tk()
    root.title("Information")
    # root.geometry("500x50+100+100")
    row = Frame(root)
    width_box = int(len(name)) + 10
    notice = Label(row, text=msg, width=width_box, font=(16), anchor='w')
    notice.pack(side=TOP)

    idCode_lb = Label(row, text="ID Code: {}".format(idCode), width=width_box, font=(16), anchor='w')
    idCode_lb.pack(side=TOP)

    name_lb = Label(row, text="Full Name: {}".format(name), width=width_box, font=(16), anchor="w")
    name_lb.pack(side = TOP)
    
    age_lb = Label(row, text="Age: {}".format(age), width=width_box, font=(16), anchor="w")
    age_lb.pack(side = TOP)

    gender_lb = Label(row, text="Gender: {}".format(gender), width=width_box, font=(16), anchor="w")
    gender_lb.pack(side = TOP)

    row.pack(side=TOP, fill=X, padx=5, pady=5)
    check = 0

    def call_ok(event=None):
        response_learning_OK(msg, person)
        root.quit()
        root.destroy()

    def call_cancel(event=None):
        global STATUS
        STATUS = STATUS_INPROGRESS
        root.quit()
        root.destroy()
    btn_ok = Button(root, text="Accept", width=10, command=call_ok)
    btn_ok.pack(side=LEFT, padx=5, pady=5)
    btn_cancel = Button(root, text="Cancel", width=10, command=call_cancel)
    btn_cancel.pack(side=RIGHT, padx=5, pady=5)
    root.bind('<Return>', call_ok)
    root.bind('<Escape>', call_cancel)
    center(root)
    root.mainloop()
    # root.destroy()
def get_information(idCode):
    global STATUS
    STATUS = STATUS_INPROGRESS
    label = None
    root = Tk()
    root.title("New Person")
    # root.geometry("500x50+100+100")
    row = Frame(root)
    idCode_lb = Label(row, text="ID Code: {}".format(idCode), width=30, font=(16), anchor='w')
    # e1.grid(row=0, column = 1)
    
    idCode_lb.pack(side=TOP)

    name_lb = Label(row, text="Full Name", width=12, font=(16), anchor="w")
    name_lb.pack(side = TOP)

    name_txt = Entry(row, width=18, font=16)
    name_txt.pack(side=TOP, expand=YES, fill=X)
    
    age_lb = Label(row, text="Age", width=12, font=(16), anchor="w")
    age_lb.pack(side = TOP)

    age_txt = Entry(row, width=18, font=16)
    age_txt.pack(side=TOP, expand=YES, fill=X)

    gender_lb = Label(row, text="Gender", width=12, font=(16), anchor="w")
    gender_lb.pack(side = TOP)

    gender_txt = Entry(row, width=18, font=16)
    gender_txt.pack(side=TOP, expand=YES, fill=X)

    row.pack(side=TOP, fill=X, padx=5, pady=5)
    check = 0

    def call_ok(event=None):
        if STATUS == STATUS_CONFIRM:
            return
        if len(name_txt.get()) == 0 or len(age_txt.get()) == 0 or len(gender_txt.get()) == 0:
            get_information(idCode)
        new_person = Person(name=name_txt.get(), age= int(age_txt.get()), gender=gender_txt.get(), idcode=idCode)
        # root.quit()
        show_information(vision_config.NEW_LEARNING_MSG, new_person)
        
        if STATUS == STATUS_DONE:
            root.destroy()

    def call_cancel(event=None):
        if STATUS == STATUS_CONFIRM:
            return
        response_cancel()
        root.destroy()
    btn_ok = Button(root, text="OK", width=10, command=call_ok)
    btn_ok.pack(side=LEFT, padx=5, pady=5)
    btn_cancel = Button(root, text="Cancel", width=10, command=call_cancel)
    btn_cancel.pack(side=RIGHT, padx=5, pady=5)
    root.bind('<Return>', call_ok)
    root.bind('<Escape>', call_cancel)
    center(root)
    root.mainloop()
    # root.destroy()


def get_idCode(database):
    global STATUS, label, db
    db = database
    STATUS = STATUS_INPROGRESS
    label = None
    root = Tk()
    root.title("Log in")
    # root.geometry("500x50+100+100")
    row = Frame(root)
    idCode_lb = Label(row, text="ID Code", width=12, font=(16), anchor='w')
    idCode_txt = Entry(row, width=18, font=16)
    # e1.grid(row=0, column = 1)
    
    idCode_lb.pack(side=TOP)
    idCode_txt.pack(side=TOP, expand=YES, fill=X)
    idCode_txt.focus_set()

    row.pack(side=TOP, fill=X, padx=5, pady=5)
    check = 0

    def call_ok(event=None):
        idCode = idCode_txt.get()
        if not str.isdigit(idCode):
            return
        idCode = int(idCode)
        root.destroy()
        response_idCode_OK(idCode)
        

    def call_cancel(event=None):
        response_cancel()
        root.destroy()
    btn_ok = Button(root, text="OK", width=10, command=call_ok)
    btn_ok.pack(side=LEFT, padx=5, pady=5)
    btn_cancel = Button(root, text="Cancel", width=10, command=call_cancel)
    btn_cancel.pack(side=RIGHT, padx=5, pady=5)
    root.bind('<Return>', call_ok)
    root.bind('<Escape>', call_cancel)
    center(root)
    root.mainloop()
    # root.destroy()
if __name__ =="__main__":
    get_idCode()
# layout_text()