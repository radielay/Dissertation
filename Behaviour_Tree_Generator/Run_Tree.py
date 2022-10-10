import copy
import json
import tkinter
from tkinter.filedialog import askopenfile
from anytree import *
import pymysql
import ChatBot as Bot
import Encryption as Encrypt
from tkinter import *
from tkinter.ttk import *
import Generator
from Generator import *

db_login = []
all_data = []

"---------------------------------------- File Popup ------------------------------------------------------------"


popup = Tk()
popup.title("Select file with Behaviour Tree data")
popup.geometry("400x200")

name = StringVar()
path = StringVar()
message = StringVar()

file_name = Label(popup, textvariable=name, foreground="NavyBlue")
file_name.place(relx=0.75, rely=0.25, anchor=CENTER)

prompt = Label(popup, text='Select Behaviour Tree Data File')
prompt.place(relx=0.4, rely=0.4, anchor=CENTER)

select_btn = Button(popup, text='Select File', command=lambda: select_file())
select_btn.place(relx=0.75, rely=0.4, anchor=CENTER)

continue_btn = Button(popup, text='Continue', command=lambda: continue_pressed())
continue_btn.place(relx=0.5, rely=0.7, anchor=CENTER)

error = Label(popup, textvariable=message, foreground="DarkRed")
error.place(relx=0.5, rely=0.9, anchor=CENTER)


def select_file():
    file_path = askopenfile(mode='r', filetypes=[('Text File', '.txt')])

    if file_path is not None:
        file_path = str(file_path)
        split_path = file_path.split("'")
        item_path = split_path[1]      # Extract file path from system path
        path.set(item_path)

        split_path = item_path.split("/")
        new_name = split_path[len(split_path)-1]  # Extract file name
        name.set(new_name)
        pass


def continue_pressed():
    global all_data

    selected_file = name.get()
    if selected_file != "":
        popup.destroy()
        tree_data = read_tree_data(selected_file)

        global db_login
        if len(db_login) >= 4:
            get_database_values(db_login[0], db_login[1], db_login[2], db_login[3], db_login[4])

        all_data = copy.deepcopy(tree_data)
        query_popup()

    else:
        message.set("Please select a file before you continue")


def query_popup():
    q_popup = Tk()
    q_popup.title("Select file with Behaviour Tree data")
    q_popup.geometry("400x200")

    bot_value = IntVar()

    bot_check = tkinter.Checkbutton(q_popup, text="Run the tree with the ChatBot", variable=bot_value, onvalue=1, offvalue=0)
    bot_check.place(relx=0.25, rely=0.3, anchor=CENTER)

    tag_label = Label(q_popup, text="BT Trigger Tag")
    tag_label.place(relx=0.2, rely=0.5, anchor=CENTER)

    tag_name = Text(q_popup, height=1.2, width=20)
    tag_name.place(relx=0.65, rely=0.5, anchor=CENTER)

    start = Button(q_popup, text="Start", command=lambda: start_pressed())
    start.place(relx=0.65, rely=0.7, anchor=CENTER)

    def start_pressed():
        global all_data
        all_nodes = []
        ticked = []

        if bot_value.get() == 1:
            trigger = tag_name.get(1.0, "end")
            trigger = trigger.replace("\n", "")

            if len(trigger) > 3:
                q_popup.destroy()
                print(" ")
                print("Welcome to the Delivery Tracking Services Bot. Should you need human assistance, just write 'quit'.")

                tree_data = run_bot(all_data, trigger)
                Encrypt.main()  # Encrypt the conversation immediately

                for item in tree_data:
                    all_nodes.append(item.name)
                    if item.ticked is True:
                        if item.name not in ticked:
                            ticked.append(item.name)

                progress = progress_window(all_nodes, ticked)
                progress.mainloop()
        else:
            q_popup.destroy()
            tree_data = big_traverse(all_data)

            for item in tree_data:
                all_nodes.append(item.name)
                if item.ticked is True:
                    if item.name not in ticked:
                        ticked.append(item.name)

            progress = progress_window(all_nodes, ticked)
            progress.mainloop()


"-------------------------------------- Run Tree from File --------------------------------------------------------"


def read_tree_data(selected_file):
    node_data = []
    nodes_children = []
    db_data = []
    nodes = []

    with open(selected_file) as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            count += 1
            if count == 1:
                data = line
                data = data.replace("'", "")
                nodes = data.split(",")

            elif count == 3:
                if line != "":
                    db_data.append(line)
            elif count == 4:
                if line != "":
                    db_data.append(line)
            elif count == 5:
                db_data.append(line)   # password can be none
            elif count == 6:
                if line != "":
                    db_data.append(line)
            elif count == 7:
                if line != "":
                    db_data.append(line)

    if len(db_data) > 1:
        for i in range(0, len(db_data)):
            db_data[i] = db_data[i].replace("\n", "")

        global db_login
        db_login = copy.deepcopy(db_data)

    for i in range(0, len(nodes)):
        if i % 2 == 0:   # even number positions = node data
            data = nodes[i].replace(":", ",")
            data = data.split(",")
            node_data.append(data)

        else:    # odd number positions are the node's children
            children = nodes[i]
            if children != 0:
                children = children.replace(":", ",")
                children = children.split(",")

            nodes_children.append(children)

    node_data.remove(node_data[len(node_data) - 1])
    tree_data = []

    for i in range(0, len(node_data)):

        obj = Board()
        item = node_data[i]
        obj.name = item[0]
        obj.type = item[1]
        obj.parent = item[2]
        obj.ticked = False
        obj.action = item[3]

        children = nodes_children[i]
        for c in range(0, len(children)):
            if children[c] == 0:
                children = 0
            else:
                children[c] = children[c].replace(" ", "")

        obj.children = children
        tree_data.append(obj)

    return tree_data


popup.mainloop()


