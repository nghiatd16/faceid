from tkinter import *
import _thread
import time

STATUS_INACTIVE = 0
STATUS_INPROGRESS = 1
STATUS_DONE = 2
STATUS = STATUS_INACTIVE
label = None

def response_OK(text):
    global STATUS, label
    label = text
    print(label)
    STATUS = STATUS_DONE

def response_cancel():
    global STATUS
    STATUS = STATUS_INACTIVE
    label = None

def reset():
    global STATUS
    STATUS = STATUS_INACTIVE
    label = None

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


def layout_text():
    global STATUS
    STATUS = STATUS_INPROGRESS
    label = None
    root = Tk()
    root.title("Thong Tin Nhan Vien")
    # root.geometry("500x50+100+100")
    row = Frame(root)
    lab = Label(row, text="Ma Nhan Vien", width=12, font=(16), anchor='w')
    ent = Entry(row, width=18, font=16)
    # e1.grid(row=0, column = 1)
    row.pack(side=TOP, fill=X, padx=5, pady=5)
    lab.pack(side=LEFT)
    ent.pack(side=RIGHT, expand=YES, fill=X)
    ent.focus_set()
    check = 0

    def call_ok(event=None):
        if(len(ent.get()) == 0):
            return
        response_OK(ent.get())
        root.quit()

    def call_cancel(event=None):
        response_cancel()
        root.quit()
    btn_ok = Button(root, text="OK", width=10, command=call_ok)
    btn_ok.pack(side=LEFT, padx=5, pady=5)
    btn_cancel = Button(root, text="Cancel", width=10, command=call_cancel)
    btn_cancel.pack(side=RIGHT, padx=5, pady=5)
    root.bind('<Return>', call_ok)
    root.bind('<Escape>', call_cancel)
    center(root)
    root.mainloop()
    root.destroy()
# layout_text()