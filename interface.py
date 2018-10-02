from tkinter import *
from tkinter import filedialog
import _thread
import time
import vision_config
import logging
import manage_data
from interact_database_v2 import Database
from object_DL import Person
from PIL import Image, ImageTk
STATUS_INACTIVE = 0
STATUS_INPROGRESS = 1
STATUS_DONE = 2
STATUS = STATUS_INACTIVE
STATUS_CONFIRM = 3
result = None
msg_result = None
msg_iden_review = None
showing_admin_review = False
db = None
# db = Database(vision_config.DB_HOST, vision_config.DB_USER, vision_config.DB_PASSWD, vision_config.DB_NAME)
def response_idCode_OK(idCode):
    person = db.getPersonByIdCode(idCode)
    if person is None:
        get_information(idCode)
    else:
        show_information(vision_config.TRANSFER_LEARNING_MSG, person)
    # STATUS = STATUS_DONE

def response_learning_OK(msg, person):
    global STATUS, result, msg_result
    logging.info("{} | person {}".format(msg, person))
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
    global STATUS
    name = person.name
    idCode = person.idcode
    birthday = person.birthday
    gender = person.gender
    country = person.country
    description = person.description
    b64img = person.b64image
    STATUS = STATUS_CONFIRM
    label = None
    root = None
    if msg == vision_config.TRANSFER_LEARNING_MSG:
        root = Tk()
    else:
        root = Toplevel()
    root.title("Information")
    # root.geometry("500x50+100+100")
    # row = Frame(root)
    width_box = int(len(name)) + 15
    
    im = Image.open("assets/unk_avt.jpg")
    if b64img is not None:
        img_ar = manage_data.convert_b64_to_image(b64img, to_rgb=True)
        im = Image.fromarray(img_ar)
    tkimage = ImageTk.PhotoImage(im)
    avt = Label(root, image=tkimage)
    avt.pack(side=TOP)
    notice = Label(root, text=msg, width=width_box, font=(16), anchor='w')
    notice.pack(side=TOP)
    idCode_lb = Label(root, text="ID Code: {}".format(idCode), width=width_box, font=(16), anchor='w')
    idCode_lb.pack(side=TOP)

    name_lb = Label(root, text="Full Name: {}".format(name), width=width_box, font=(16), anchor="w")
    name_lb.pack(side = TOP)
    
    birthday_lb = Label(root, text="Birthday: {}".format(manage_data.convert_date_format(birthday)), width=width_box, font=(16), anchor="w")
    birthday_lb.pack(side = TOP)

    gender_lb = Label(root, text="Gender: {}".format(gender), width=width_box, font=(16), anchor="w")
    gender_lb.pack(side = TOP)

    country_lb = Label(root, text="Country: {}".format(country), width=width_box, font=(16), anchor="w")
    country_lb.pack(side = TOP)

    des_lb = Label(root, text="Description: {}".format(description), width=width_box, font=(16), anchor="w")
    des_lb.pack(side = TOP)

    # root.pack(side=TOP, fill=X, padx=5, pady=5)
    check = 0

    def call_ok(event=None):
        response_learning_OK(msg, person)
        root.quit()
        root.destroy()

    def call_cancel(event=None):
        global STATUS
        STATUS = STATUS_INPROGRESS
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
    # row = Frame(root)
    width = min(max(10 + len(str(idCode)), 25), 50)
    idCode_lb = Label(root, text="ID Code: {}".format(idCode), width=width, font=(16), anchor='w')
    # e1.grid(row=0, column = 1)
    idCode_lb.grid(row=0, column=0)
    avt_path = Label(root, text="")
    im = Image.open("assets/unk_avt.jpg")
    tkimage = ImageTk.PhotoImage(im)
    # Label(root, text = "Mori").grid(row = 0, column=0)
    avt = Label(root, image=tkimage)
    avt.grid(row = 0, column=1)
    name_lb = Label(root, text="Full Name", width=width, font=(16), anchor="w")
    name_lb.grid(row=2, column=0)

    name_txt = Entry(root, width=width, font=16)
    name_txt.grid(row=2, column=1)
    name_txt.focus_set()

    birthday_lb = Label(root, text="Date of Birth", width=width, font=(16), anchor="w")
    birthday_lb.grid(row=3, column=0)

    birthday_txt = Entry(root, width=width, font=16)
    birthday_txt.grid(row=3, column=1)

    gender_lb = Label(root, text="Gender", width=width, font=(16), anchor="w")
    gender_lb.grid(row=4, column=0)

    gender_txt = Entry(root, width=width, font=16)
    gender_txt.grid(row=4, column=1)

    country_lb = Label(root, text="Country", width=width, font=(16), anchor="w")
    country_lb.grid(row=5, column=0)

    country_txt = Entry(root, width=width, font=16)
    country_txt.grid(row=5, column=1)

    des_lb = Label(root, text="Description", width=width, font=(16), anchor="w")
    des_lb.grid(row=6, column=0)
    
    des_txt = Entry(root, width=width, font=16)
    des_txt.grid(row=6, column=1)
    
    check = 0

    def call_ok(event=None):
        global STATUS
        if STATUS == STATUS_CONFIRM:
            return
        if len(name_txt.get()) == 0:
            name_txt.focus_set()
            return
        if len(birthday_txt.get()) == 0:
            birthday_txt.focus_set()
            return
        if len(gender_txt.get()) == 0:
            gender_txt.focus_set()
            return
        if len(country_txt.get()) == 0:
            country_txt.focus_set()
            return
        if len(des_txt.get()) == 0:
            des_txt.focus_set()
            return
        birthday = manage_data.std_date_format(birthday_txt.get())
        if birthday == "-1":
            return
        b64img = None
        path = avt_path.cget("text")
        if path != "":
            b64img = manage_data.load_b64_img(path)
        new_person = Person(name=name_txt.get(), birthday= birthday, gender=gender_txt.get(), idcode=idCode, country=country_txt.get(), description=des_txt.get(), b64image=b64img)
        # root.quit()
        show_information(vision_config.NEW_LEARNING_MSG, new_person)
        if STATUS == STATUS_DONE:
            root.quit()
            root.destroy()
            # STATUS = STATUS_INACTIVE

    def call_cancel(event=None):
        global STATUS
        if STATUS == STATUS_CONFIRM:
            return
        response_cancel()
        root.destroy()
    def browsefunc(avt):
        try:
            path = filedialog.askopenfilename()
            img = Image.open(path)
            img = img.resize((150, 150))
            photo=ImageTk.PhotoImage(img)
            avt.configure(image=photo)
            avt.image = photo
            avt_path.configure(text=path)
        except Exception as e:
            logging.exception(e)
            avt_path.configure(text="")
            pass

    btn_browse = Button(root, text="Browse", command=lambda: browsefunc(avt), anchor="w")
    btn_browse.grid(row=1, column=1)
    btn_ok = Button(root, text="OK", width=10, command=call_ok)
    btn_ok.grid(row=7, column=0)
    btn_cancel = Button(root, text="Cancel", width=10, command=call_cancel)
    btn_cancel.grid(row=7, column=1)
    # row.grid()
    root.bind('<Return>', call_ok)
    root.bind('<Escape>', call_cancel)
    center(root)
    root.mainloop()
    # root.destroy()


def identification_review(database=None, multi_tracker=None):
    global msg_iden_review
    root = Tk()
    root.title("Identification Admin Review")
    # root.geometry("500x50+100+100")
    row = Frame(root)
    width_box = 30
    # notice = Label(row, text="Identification Admin Review", width=width_box, font=(16), anchor='w')
    # notice.pack(side=TOP)
    def call_ok(msg):
        global msg_iden_review
        # msg_iden_review = msg
        # tracker = multi_tracker.get_multitracker()[0]
        # person = database.getPersonByName(msg)
        # tracker.person = person
        print(msg)
    def call_cancel(event=None):
        global STATUS, showing_admin_review
        STATUS = STATUS_INPROGRESS
        showing_admin_review = False
        root.destroy()
    TIS_VIP = ["Toru Kuwano", "Kiyotaka Nakamura", "Hiromitsu Fujino", "Osamu Ishiguro", "Masahiro Mori", "Kensaku Furusho", "Dang Anh Trung"]
    TV_VIP = ["Hoang To", "Nguyen Quan Son", "Nguyen Khanh Hoan", "Nguyen Son Tung", "Tham Duc Thang", "Nguyen Ich Vinh", "Pham Thuc Truong Luong"]
    
    #TIS VIP
    Button(root, text="Mr.Toru Kuwano", width=30, height = 5, command=lambda: call_ok(TIS_VIP[0])).grid(row=0,column=0)
    Button(root, text="Mr.Kiyotaka Nakamura", width=30, height = 5, command=lambda: call_ok(TIS_VIP[1])).grid(row=1,column=0)
    Button(root, text="Mr.Hiromitsu Fujino", width=30, height = 5, command=lambda: call_ok(TIS_VIP[2])).grid(row=2,column=0)
    Button(root, text="Mr.Osamu Ishiguro", width=30, height = 5, command=lambda: call_ok(TIS_VIP[3])).grid(row=3,column=0)
    Button(root, text="Mr.Masahiro Mori", width=30, height = 5, command=lambda: call_ok(TIS_VIP[4])).grid(row=4,column=0)
    Button(root, text="Mr.Kensaku Furusho", width=30, height = 5, command=lambda: call_ok(TIS_VIP[5])).grid(row=5,column=0)
    Button(root, text="Mr.Dang Anh Trung", width=30, height = 5, command=lambda: call_ok(TIS_VIP[6])).grid(row=6,column=0)
    
    #TV_VIP
    Button(root, text="Mr.Hoang To", width=30, height = 5, command=lambda: call_ok(TV_VIP[0])).grid(row=0,column=1)
    Button(root, text="Mr.Nguyen Quan Son", width=30, height = 5, command=lambda: call_ok(TV_VIP[1])).grid(row=1,column=1)
    Button(root, text="Mr.Nguyen Khanh Hoan", width=30, height = 5, command=lambda: call_ok(TV_VIP[2])).grid(row=2,column=1)
    Button(root, text="Mr.Nguyen Son Tung", width=30, height = 5, command=lambda: call_ok(TV_VIP[3])).grid(row=3,column=1)
    Button(root, text="Mr.Tham Duc Thang", width=30, height = 5, command=lambda: call_ok(TV_VIP[4])).grid(row=4,column=1)
    Button(root, text="Mr.Nguyen Ich Vinh", width=30, height = 5, command=lambda: call_ok(TV_VIP[5])).grid(row=5,column=1)
    Button(root, text="Mr.Pham Thuc Truong Luong", width=30, height = 5, command=lambda: call_ok(TV_VIP[6])).grid(row=6,column=1)

    Label(root, text="Custom Name", width=30, font=(16), anchor='w').grid(row=7, column=0)
    custom_txt = Entry(root, width=30, font=16)
    custom_txt.grid(row=7, column=1)
    btn_ok = Button(root, text="OK", width=30, height = 3, command=lambda: call_ok(custom_txt.get())).grid(row=8,column=1)
    root.bind('<Return>', call_cancel)
    root.bind('<Escape>', call_cancel)
    center(root)
    root.mainloop()

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
    db = Database(vision_config.DB_HOST, vision_config.DB_USER, vision_config.DB_PASSWD, vision_config.DB_NAME)
    get_idCode(db)
# layout_text()
