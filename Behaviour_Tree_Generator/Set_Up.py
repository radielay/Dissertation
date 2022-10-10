import tkinter
from tkinter.filedialog import askopenfile
import Generator
from Generator import *

tree_data = []
selection_made = False
db_data = []


def write_to_file(data, new_name):

    file = open(new_name, "w")
    new_data = ""

    def transform_str(string):
        string = string.replace(",", ":")
        string = string.replace("]", "")
        string = string.replace("[", "")

        return string

    for item in data:
        item.action = item.action.replace('\n', '')
        node_data = [item.name, item.type, item.parent, item.action]  # gather all the tree data
        node_children = str(item.children)

        node_data = str(node_data)
        node_data = transform_str(node_data)
        node_children = transform_str(node_children)

        new_data += node_data
        new_data += ","
        new_data += node_children
        new_data += ","

    new_data.replace("'", "")
    file.write(new_data)
    file.write("\n")

    for item in db_data:
        file.write('\n' + item)

    file.close()


"""------------------------------------- Pop up Start Window ------------------------------------------------------------"""

popup = Tk()
popup.title("Select JSON file of a behavior tree")
popup.geometry("400x200")

name = StringVar()
path = StringVar()

file_name = Label(popup, textvariable=name, foreground="NavyBlue")
file_name.place(relx=0.75, rely=0.25, anchor=CENTER)

prompt = Label(popup, text='Select JSON Behaviour Tree File')
prompt.place(relx=0.4, rely=0.4, anchor=CENTER)

select_btn = Button(popup, text='Select File', command=lambda: select_file())
select_btn.place(relx=0.75, rely=0.4, anchor=CENTER)

continue_btn = Button(popup, text='Continue', command=lambda: continue_pressed())
continue_btn.place(relx=0.5, rely=0.7, anchor=CENTER)


def select_file():
    file_path = askopenfile(mode='r', filetypes=[('Json File', '.json')])

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
    global tree_data

    file = path.get()
    if file != "":
        popup.destroy()

        all_nodes = Generator.generate_tree(file)
        tree_data = all_nodes

        nodes = sort_nodes(tree_data)
        main_window(nodes)

    else:
        error = Label(popup, text="Please select a JSON file before you continue", foreground='DarkRed')
        error.place(relx=0.5, rely=0.85, anchor=CENTER)


"""-------------------- Enter Database credentials for default function ------------------------------------------"""


def db_popup():
    db_window = Tk()
    db_window.title("Save your database credentials")
    db_window.geometry("440x240")

    err = StringVar()

    label1 = Label(db_window, text="Host name")
    label1.place(relx=0.15, rely=0.2, anchor=CENTER)

    host_name = Text(db_window, height=1.2, width=20)
    host_name.place(relx=0.6, rely=0.2, anchor=CENTER)

    label2 = Label(db_window, text="Username")
    label2.place(relx=0.15, rely=0.3, anchor=CENTER)

    username = Text(db_window, height=1.2, width=20)
    username.place(relx=0.6, rely=0.3, anchor=CENTER)

    label3 = Label(db_window, text="Password")
    label3.place(relx=0.15, rely=0.4, anchor=CENTER)

    pas = Text(db_window, height=1.2, width=20)
    pas.place(relx=0.6, rely=0.4, anchor=CENTER)

    label4 = Label(db_window, text="Database name")
    label4.place(relx=0.15, rely=0.5, anchor=CENTER)

    db_name = Text(db_window, height=1.2, width=20)
    db_name.place(relx=0.6, rely=0.5, anchor=CENTER)

    label6 = Label(db_window, text="Table name")
    label6.place(relx=0.15, rely=0.6, anchor=CENTER)

    table_name = Text(db_window, height=1.2, width=20)
    table_name.place(relx=0.6, rely=0.6, anchor=CENTER)

    next_btn2 = Button(db_window, text="Next", command=lambda: next2_pressed())
    next_btn2.place(relx=0.8, rely=0.8, anchor=CENTER)

    label7 = Label(db_window, textvariable=err, foreground="DarkRed")  #not working
    label7.place(relx=0.1, rely=0.95, anchor=CENTER)

    def next2_pressed():
        host1 = host_name.get(1.0, "end")
        user1 = username.get(1.0, "end")
        pas1 = pas.get(1.0, "end")
        db = db_name.get(1.0, "end")
        table1 = table_name.get(1.0, "end")

        if len(host1) > 2:
            if len(user1) > 2:
                if len(db) > 2:
                    if len(table1) > 2:

                        db_credentials = [host1, user1, pas1, db, table1]
                        for i in range(0, len(db_credentials)):
                            db_credentials[i] = db_credentials[i].replace("\n", "")
                            db_credentials[i] = db_credentials[i].replace("\t", "")
                        # print(db_credentials)

                        global db_data
                        db_data = copy.deepcopy(db_credentials)
                        db_window.destroy()
                    else:
                        err.set("Please insert table name")
                        print(err.get())
                else:
                    err.set("Please insert database name")
                    print(err.get())
            else:
                err.set("Please insert your username (example: root)")
                print(err.get())
        else:
            err.set("Please insert the name of your database host (example: localhost)")
            print(err.get())

    db_window.mainloop()


"""------------------------------------------- Main Window ------------------------------------------------------"""


def sort_nodes(nodes):   # Only include action nodes to the drop-down menu

    action_nodes = ["Default"]
    for item in nodes:
        if item.type != "selector":
            if item.type != "sequence":
                if item.type != "parallel":
                    action_nodes.append(item.name)

    return action_nodes


def main_window(nodes):
    window = Tk()
    window.title("Setting up your behaviour tree")
    window.geometry("700x400")

    message = StringVar()
    success = StringVar()
    selected = StringVar(window)

    db_value = IntVar()
    test_value = IntVar()

    label1 = Label(window, text="Select node", foreground="NavyBlue")
    label1.place(relx=0.15, rely=0.15, anchor=CENTER)

    label2 = Label(window, text="Attach function", foreground="NavyBlue")
    label2.place(relx=0.5, rely=0.15, anchor=CENTER)

    label3 = Label(window, textvariable=message, foreground="DarkRed")
    label3.place(relx=0.58, rely=0.45, anchor=CENTER)

    label4 = Label(window, textvariable=success, foreground="green")
    label4.place(relx=0.15, rely=0.45, anchor=CENTER)

    text_area = Text(window, height=4, width=50)    # Replace with new label + button, move to new popup
    text_area.place(relx=0.65, rely=0.32, anchor=CENTER)

    connect = Button(window, text="Connect", command=lambda: connect_pressed())  # Move position
    connect.place(relx=0.5, rely=0.55, anchor=CENTER)

    clear = Button(window, text="Clear", command=lambda: clear_pressed())  # Move to new popup
    clear.place(relx=0.76, rely=0.55, anchor=CENTER)

    drop_menu = OptionMenu(window, selected, *nodes)
    drop_menu.place(relx=0.15, rely=0.25, anchor=CENTER)

    next_button = Button(window, text="Next", command=lambda: next_pressed())
    next_button.place(relx=0.8, rely=0.8, anchor=CENTER)

    test_check = tkinter.Checkbutton(window, text="Test Run the tree (recommended)", variable=test_value, onvalue=1,
                                     offvalue=0)
    test_check.place(relx=0.15, rely=0.65, anchor=CENTER)

    db_check = tkinter.Checkbutton(window, text="Use default database function", variable=db_value, onvalue=1,
                                   offvalue=0, command=lambda: check_db_box())
    db_check.place(relx=0.135, rely=0.75, anchor=CENTER)

    def check_db_box():
        if db_value.get() == 1:
            db_popup()

    def change_value(*args):

        action_node = selected.get()    # SELECTED from DROP DOWN
        success.set("")

        global selection_made
        selection_made = True

        for item in tree_data:
            if item.name == action_node:
                text_area.delete(1.0, "end")
                text_area.insert(1.0, item.action)  # Get the function of the item if any and display it

    selected.trace('w', change_value)

    def clear_pressed():
        text_area.delete(1.0, "end")

    def connect_pressed():
        action_node = selected.get()
        if selection_made is True:
            action = text_area.get(1.0, "end")
            if len(action) > 1:
                global tree_data
                tree_data = connect_node(tree_data, action_node, action)

                message.set("")
                success.set("Successfully connected")
            else:
                message.set("Please enter a function to attach to the selected node")
        else:
            message.set("Please select an action node")

    def next_pressed():
        global tree_data

        if selection_made is False:
            message.set("Please select an action node")
        else:
            text = text_area.get(1.0, "end")
            if len(text) > 1:
                window.destroy()

                if test_value.get() == 1:
                    global db_data
                    if len(db_data) >= 4:
                        get_database_values(db_data[0], db_data[1], db_data[2], db_data[3], db_data[4])
                    tree_data = Generator.big_traverse(tree_data)

                    all_nodes = []
                    ticked = []
                    for item in tree_data:
                        all_nodes.append(item.name)
                        if item.ticked is True:
                            if item.name not in ticked:
                                ticked.append(item.name)

                    progress = progress_window(all_nodes, ticked)
                    progress.mainloop()
                save_popup()

            else:
                message.set("Please enter a function to attach to the selected node")

    window.mainloop()


"""----------------------------------------  Save File Popup -----------------------------------------------------"""


def save_popup():
    new_popup = Tk()
    new_popup.title("Save your behaviour tree")
    new_popup.geometry("400x200")

    prompt_name = Label(new_popup, text='Save your file as:')
    prompt_name.place(relx=0.2, rely=0.3, anchor=CENTER)

    name_field = Text(new_popup, height=1.2, width=20)
    name_field.place(relx=0.65, rely=0.32, anchor=CENTER)

    save_btn = Button(new_popup, text='Save', command=lambda: save_pressed())
    save_btn.place(relx=0.6, rely=0.6, anchor=CENTER)

    error = StringVar()
    label = Label(new_popup, textvariable=error, foreground="DarkRed")
    label.place(relx=0.6, rely=0.8, anchor=CENTER)

    def save_pressed():
        new_name = name_field.get(1.0, "end")

        if len(new_name) > 1:
            new_name = new_name.replace("\n", "")
            new_name += ".txt"

            write_to_file(tree_data, new_name)
            new_popup.destroy()

        else:
            error.set("Please enter a name for your file")

    new_popup.mainloop()


popup.mainloop()
