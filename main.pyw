from tkinter import *
import sqlite3
import os
from threading import *
from tkinter import ttk
import re
import tkinter.messagebox as tmsg

email_validator = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def validatePhoneNumber(s):
    Pattern = re.compile(r'^\+\d{1,3}\d{6,12}$')
    return Pattern.match(s)

def update_Values():
    conn = sqlite3.connect("contact_book.db")
    cur = conn.cursor()
    int_id = int(userID)
    cur.execute("SELECT * FROM contacts WHERE oid=?", (int_id,))
    result = cur.fetchone()
    if result != None :
        if edit_name.get() and edit_phone.get() and edit_email.get() and edit_addr.get() != "" :
            if validatePhoneNumber(edit_phone.get()) :
                if re.fullmatch(email_validator, edit_email.get()) :
                    try:
                        cur.execute("""UPDATE contacts SET
                        name = :newName,
                        ph_number = :newPhoneNum,
                        email = :newEmail,
                        address = :newAddress
                        WHERE oid = :oid""",
                        {
                            'newName': edit_name.get(),
                            'newPhoneNum': edit_phone.get(),
                            'newEmail': edit_email.get(),
                            'newAddress': edit_addr.get(),
                            'oid': userID
                        })
                        conn.commit()
                        conn.close()
                        status_editPanel.configure(text="Updated", fg="green")
                        showContactList()
                    except:
                        status_editPanel.configure(text="Something went wrong!", fg="red")
                else:
                    status_editPanel.configure(text="Invalid Email!", fg="red")
            else:
                status_editPanel.configure(text="Invalid Phone Number! Use with country code", fg="red")

        else:
            status_editPanel.configure(text="Empty field cannot updated!", fg="red")

    else:
        status_editPanel.configure(text="User ID not found!", fg="red")
# checking the existence of contact list
def checkValidityForUpdateWin():
    try:
        conn = sqlite3.connect("contact_book.db")
        cur = conn.cursor()
        cur.execute("SELECT *, oid FROM contacts")
        all_contacts = cur.fetchall()

        if len(all_contacts) != 0 :
            if modifyConVal.get() != "" :
                # validating the existence of the selected ID
                int_id = int(modifyConVal.get())
                cur.execute("SELECT * FROM contacts WHERE oid=?", (int_id,))
                result = cur.fetchone()
                if result != None :
                    edit_btn_panel['state'] = NORMAL
                    edit_btn_panel.configure(bg="#7469B6")
                    editUser()
                else:
                    tmsg.showerror("Error", "User ID not found!")
            else:
                tmsg.showerror("Error", "No ID has been selected!")
        else:
            tmsg.showerror("Error", "Empty contact list")
            edit_btn_panel['state'] = DISABLED
            edit_btn_panel.configure(bg="gray")

        conn.commit()
        conn.close()
    except:
        tmsg.showerror("Error", "Something went wrong!")
# edit user contact panel
def editUser():
    edit_panel = Tk()
    edit_panel.geometry("700x400")
    edit_panel.maxsize(700, 400)
    edit_panel.minsize(700, 400)
    edit_panel.title("Update credentials")

    conn = sqlite3.connect("contact_book.db")
    cur = conn.cursor()

    global userID
    userID = modifyConVal.get()

    cur.execute("SELECT * FROM contacts WHERE oid = " + userID)
    all_contacts = cur.fetchall()
    Label(edit_panel, text="Update Credentials", font="Roboto 20 bold", fg="#0ABA79").grid(row=0, column=0, sticky=W, padx=15, pady=40)
    Label(edit_panel, text="Name", font=labels_font).grid(row=1, column=0, sticky=W, padx=15)
    Label(edit_panel, text="Phone Number", font=labels_font).grid(row=2, column=0, sticky=W, padx=15)
    Label(edit_panel, text="Email", font=labels_font).grid(row=3, column=0, sticky=W, padx=15)
    Label(edit_panel, text="Address", font=labels_font).grid(row=4, column=0, sticky=W, padx=15)
    Label(edit_panel, text=":", font=labels_font).grid(row=1, column=1, sticky=E, padx=2)
    Label(edit_panel, text=":", font=labels_font).grid(row=2, column=1, sticky=E, padx=2)
    Label(edit_panel, text=":", font=labels_font).grid(row=3, column=1, sticky=E, padx=2)
    Label(edit_panel, text=":", font=labels_font).grid(row=4, column=1, sticky=E, padx=2)

    global edit_name
    global edit_phone
    global edit_email
    global edit_addr
    global status_editPanel

    edit_name = Entry(edit_panel, width=34, font=entries_font)
    edit_name.grid(row=1, column=2, pady=7)
    edit_phone = Entry(edit_panel, width=34, font=entries_font)
    edit_phone.grid(row=2, column=2, pady=7)
    edit_email = Entry(edit_panel, width=34, font=entries_font)
    edit_email.grid(row=3, column=2, pady=7)
    edit_addr = Entry(edit_panel, width=34, font=entries_font)
    edit_addr.grid(row=4, column=2, pady=7)
    Button(edit_panel, text="Update", command=update_Values, padx=20, font="Roboto 10 bold", bg="#0ABA79").grid(row=5, column=0, sticky=W, padx=15, pady=15)
    status_editPanel = Label(edit_panel, text="", font="Roboto 10 bold")
    status_editPanel.grid(row=5, column=2, sticky=W)
    

    for users in all_contacts:
        edit_name.insert(0, users[0])
        edit_phone.insert(0, users[1])
        edit_email.insert(0, users[2])
        edit_addr.insert(0, users[3])

    conn.commit()
    conn.close()
# thread for deleting user
def thread_delete():
    thr = Thread(target=deleteUser)
    thr.start()
# deleting user
def deleteUser():
    conn = sqlite3.connect("contact_book.db")
    cur = conn.cursor()
    if modifyConVal.get() != "" :
        askToUserDel = tmsg.askquestion("Warning", "Do you want to delete this contact?")
        if askToUserDel == "yes" :
            try:
                # validating the existence of the selected ID
                int_id = int(modifyConVal.get())
                cur.execute("SELECT * FROM contacts WHERE oid=?", (int_id,))
                result = cur.fetchone()
                if result != None :
                    cur.execute("DELETE from contacts WHERE oid = " + modifyConVal.get())
                    modifyEntry.delete(0, END)
                    tmsg.showinfo("Message", "Contact has been deleted")
                else:
                    tmsg.showerror("Error", "User ID not found")
            except:
                tmsg.showerror("Error", "Something went wrong!")
        else:
            pass
    else:
        tmsg.showerror("Error", "No ID has been selected!")

    for item in tree.get_children():
        tree.delete(item)

    cur.execute("SELECT *, oid FROM contacts")
    all_contacts = cur.fetchall()

    for contact in all_contacts:
        tree.insert('', 'end', values=contact)
    
    status.configure(text="")
    
    conn.commit()
    conn.close()

def clearForm():
    [widget.delete(0, END) for widget in cont_form_frame.winfo_children() if isinstance(widget, Entry)]
    status.configure(text="")

# creating thread for saving data
def thread_submit():
    thr = Thread(target=submitData)
    thr.start()

# saving contact data to database
def submitData():
    if nameVal.get() and phoneVal.get() and emailVal.get() and addrVal.get() != "" :
        if validatePhoneNumber(phoneVal.get()) :
            if re.fullmatch(email_validator, emailVal.get()) :
                try:
                    databaseExist = os.path.isfile("contact_book.db")
                    if databaseExist :
                        conn = sqlite3.connect("contact_book.db")
                        cur = conn.cursor()

                        cur.execute("INSERT INTO contacts VALUES (:name, :phone_num, :email, :address)", {
                            'name': nameVal.get(),
                            'phone_num': phoneVal.get(),
                            'email': emailVal.get(),
                            'address': addrVal.get()
                        })

                        for item in tree.get_children():
                            tree.delete(item)

                        cur.execute("SELECT *, oid FROM contacts")
                        all_contacts = cur.fetchall()

                      
                        for contact in all_contacts:
                            tree.insert('', 'end', values=contact)
                       
                        
                        conn.commit()
                        conn.close()

                        status.configure(text="Saved", fg="green")

                        [widget.delete(0, END) for widget in cont_form_frame.winfo_children() if isinstance(widget, Entry)]
                        edit_btn_panel['state'] = NORMAL
                        edit_btn_panel.configure(bg="#7469B6")

                    else:
                        conn = sqlite3.connect("contact_book.db")
                        cur = conn.cursor()
                        cur.execute(""" CREATE TABLE contacts(
                            name text,
                            ph_number text,
                            email text,
                            address text
                            )""")
                        
                        cur.execute("INSERT INTO contacts VALUES (:name, :phone_num, :email, :address)", {
                            'name': nameVal.get(),
                            'phone_num': phoneVal.get(),
                            'email': emailVal.get(),
                            'address': addrVal.get()
                        })

                        for item in tree.get_children():
                            tree.delete(item)

                        cur.execute("SELECT *, oid FROM contacts")
                        all_contacts = cur.fetchall()

                        for contact in all_contacts:
                            tree.insert('', 'end', values=contact)

                        conn.commit()
                        conn.close()

                        status.configure(text="Database created and saved data", fg="green")

                        [widget.delete(0, END) for widget in cont_form_frame.winfo_children() if isinstance(widget, Entry)]
                        edit_btn_panel['state'] = NORMAL
                        edit_btn_panel.configure(bg="#7469B6")
                except:
                    tmsg.showerror("Error", "Something went wrong")
            else:
                tmsg.showerror("Error", "Invalid Email")

        else:
            tmsg.showerror("Error", "Invalid Phone Number. Use with country code.")
    else:
        tmsg.showerror("Error", "Empty field!")

# showing contact list through this button click 
def showContactList():
    try:
        databaseExist = os.path.isfile("contact_book.db")
        if databaseExist:
            conn = sqlite3.connect("contact_book.db")
            cur = conn.cursor()

            for item in tree.get_children():
                tree.delete(item)

            cur.execute("SELECT *, oid FROM contacts")
            all_contacts = cur.fetchall()

            if len(all_contacts) != 0 :
                for contact in all_contacts:
                    tree.insert('', 'end', values=contact)
                status.configure(text="")
                edit_btn_panel['state'] = NORMAL
                edit_btn_panel.configure(bg="#7469B6")
            else:
                status.configure(text="Empty contact list", fg="red")
                tmsg.showerror("Error", "Empty contact list!")
                edit_btn_panel['state'] = DISABLED
                edit_btn_panel.configure(bg="gray")

            conn.commit()
            conn.close()
        else:
            tmsg.showerror("Error", "Database is not created. Store your first contact to create database automaticaly.")
    except:
        tmsg.showerror("Error", "Something went wrong!")


if __name__ == "__main__":

    root = Tk()
    root.geometry("1200x720")
    root.minsize(800, 500)
    root.title("Tkinter with sqlite3")

    # fonts
    font_title = "Roboto 20 bold"
    entries_font = "Roboto 15"
    labels_font = "Roboto 15 bold"

    # geometry variables
    entries_width = 42
    textarea_height = 5

    # contact book main frame
    main_frame = Frame(root)
    main_frame.pack(side=TOP, anchor=CENTER, fill=X)

    # for title packing
    header_frame = Frame(main_frame)
    header_frame.pack(side=TOP, anchor=CENTER, fill=X)

    # title of the contact boook
    Label(header_frame, text="Contact Book", font=font_title, fg="#135D66").pack(side=TOP, anchor=CENTER, pady=20)

    # contact box in a frame
    cont_form_frame = Frame(main_frame)
    cont_form_frame.pack(side=TOP, anchor=CENTER)

    # user labels
    Label(cont_form_frame, text="Name", font=labels_font).grid(row=0, column=0, sticky=W, padx=15)
    Label(cont_form_frame, text="Phone Number", font=labels_font).grid(row=1, column=0, sticky=W, padx=15)
    Label(cont_form_frame, text="Email", font=labels_font).grid(row=2, column=0, sticky=W, padx=15)
    Label(cont_form_frame, text="Address", font=labels_font).grid(row=3, column=0, sticky=W, padx=15)
    
    # colon labels
    Label(cont_form_frame, text=":", font=labels_font).grid(row=0, column=1, sticky=E, padx=2)
    Label(cont_form_frame, text=":", font=labels_font).grid(row=1, column=1, sticky=E, padx=2)
    Label(cont_form_frame, text=":", font=labels_font).grid(row=2, column=1, sticky=E, padx=2)
    Label(cont_form_frame, text=":", font=labels_font).grid(row=3, column=1, sticky=E, padx=2)

    # entry values
    nameVal = StringVar()
    phoneVal = StringVar()
    emailVal = StringVar()
    addrVal = StringVar()
    modifyConVal = StringVar()

    # user entires, includes name, phone, email, address
    Entry(cont_form_frame, width=entries_width, font=entries_font, textvariable=nameVal).grid(row=0, column=2, pady=7)
    Entry(cont_form_frame, width=entries_width, font=entries_font, textvariable=phoneVal).grid(row=1, column=2, pady=7)
    Entry(cont_form_frame, width=entries_width, font=entries_font, textvariable=emailVal).grid(row=2, column=2, pady=7)
    Entry(cont_form_frame, width=entries_width, font=entries_font, textvariable=addrVal).grid(row=3, column=2, pady=7)

    # buttons for saving contact, includes clear and save button
    btns_frame = Frame(root)
    btns_frame.pack(side=TOP, anchor=CENTER, pady=20)

    Button(btns_frame, text="Clear", font="Roboto 10 bold", bg="red", fg="white", padx=20, command=clearForm).grid(row=0, column=0, sticky=E, padx=10)

    submit_btn = Button(btns_frame, text="Save", font="Roboto 10 bold", bg="#0ABA79", fg="black", padx=20, command=submitData)
    submit_btn.grid(row=0, column=1, sticky=W, padx=10)

    # show details, edit, delete and modify entry here
    details_frame = Frame(root,pady=20)
    details_frame.pack(side=TOP, anchor=CENTER)

    Button(details_frame, text="Show contact list", bg="#003C43", fg="white", command=showContactList, padx=20, font="Roboto 10 bold").grid(row=0, column=0, sticky=W, padx=213)
    Label(details_frame, text="Select ID:", font="Roboto 14 bold").grid(row=0, column=1)
    modifyEntry = Entry(details_frame, textvariable=modifyConVal, font="Roboto 14 bold", fg="red", width=15)
    modifyEntry.grid(row=0, column=2, padx=10)
    edit_btn_panel = Button(details_frame, text="Edit", bg="#7469B6", fg="white", font="Roboto 10 bold", padx=20, command=checkValidityForUpdateWin)
    edit_btn_panel.grid(row=0, column=3, padx=10)
    Button(details_frame, text="Delete", bg="red", fg="white", font="Roboto 10 bold", padx=20, command=thread_delete).grid(row=0, column=4)
    
    # all saved contact lists here:
    list_frame = Frame(root)
    list_frame.pack(side=TOP, anchor=CENTER)

    s = ttk.Style()
    s.configure('Treeview', rowheight=25)

    tree = ttk.Treeview(list_frame, column=("c1", "c2", "c3", "c4", "c5"), show='headings', height=10)
    tree.column("# 1", anchor="nw", width=200)
    tree.heading("# 1", text="Name", anchor="sw")
    tree.column("# 2", anchor="nw", width=200)
    tree.heading("# 2", text="Phone Number", anchor="sw")
    tree.column("# 3", anchor="nw", width=200)
    tree.heading("# 3", text="Email", anchor="sw")
    tree.column("# 4", anchor="nw", width=400)
    tree.heading("# 4", text="Address", anchor="sw")
    tree.column("# 5", anchor="nw", width=50)
    tree.heading("# 5", text="ID", anchor="sw")

    tree.pack()

    status = Label(root, text="", font="Roboto 15 bold", padx=9, pady=8)
    status.pack(side=BOTTOM, anchor=CENTER, pady=10)

    root.mainloop()