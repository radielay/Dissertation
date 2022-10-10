import copy
import json
from anytree import *
import pymysql
# import ChatBot as Bot
# import Encryption as Encrypt
from tkinter import *
from tkinter.ttk import *


""" -------------------------------------- Read JSON file ------------------------------------------------------- """


def read_json(file_name):
    with open(file_name, "r") as read_file:
        d = json.load(read_file)  # Get Json (Dict.)
        data = json.dumps(d)  # Transform dict to string

    return data


"---------------Generate BT----------------Do NOT modify this section ------------------------------------------------"

nodes_ticked = []


class Board:
    """This class is used for storing json data in global memory"""
    def __init__(self):
        self.name = ""
        self.type = ""  # for repeating names
        self.children = []
        self.parent = ""
        self.ticked = False
        self.action = ""


def set_tree(data):
    """Remove redundant symbols and Structure tree nodes"""

    data = data.replace("{", "Node(")
    data = data.replace("}", ")")
    data = data.replace('"name"', 'name')
    data = data.replace('"children"', 'children')
    data = data.replace(":", " =")
    data = data.replace("_children = null,", "")

    return data


def set_data(data):
    """ The system can work with both the string names and symbols for Sequence, Selector, and Parallel nodes"""

    while "-->" in data:  # Sequence node
        data = data.replace("-->", "sequence")  # Symbols

    while "?" in data:    # Selector node
        data = data.replace("?", "selector")

    while "=3" in data:  # Parallel node
        data = data.replace("=3", "parallel")

    while "Sequence" in data:  # Sequence node
        data = data.replace("Sequence", "sequence")   # String names

    while "Selector" in data:    # Selector node
        data = data.replace("Selector", "selector")

    while "Parallel" in data:  # Parallel node
        data = data.replace("Parallel", "parallel")

    # print(data)
    return data


def index_nodes(root_data):

    root_list = root_data.split('"')
    s1 = s2 = p = 0
    for i in range(0, len(root_list)):
        if root_list[i] == "sequence":
            s1 += 1
            name = "sequence_" + str(s1)
            root_list[i] = name

        elif root_list[i] == "selector":
            s2 += 1
            name = "selector_" + str(s2)
            root_list[i] = name

        elif root_list[i] == "parallel":
            p += 1
            name = "parallel_" + str(p)
            root_list[i] = name

    root_data = '"'.join(root_list)
    return root_data


def find_children(children):

    loop = len(children)  # Record all children
    for i in range(0, loop):
        # Get the child's path
        path = str(children[i])

        # Modify the path string to extract each child's name
        path = path.replace("'", "/")
        child = path.split("/")
        # print("Child ", path)

        # Get the name
        length = len(child)
        child_node = child[length - 2]

        # Update the list
        children[i] = child_node
    # print("All children ", children)

    return children


def find_parent(parent_path):

    loop = len(parent_path)
    parent = ""
    for i in range(0, loop):
        # Get the parent's path
        path = str(parent_path[i])

        # Modify the path string to extract parent's name
        path = path.replace("'", "/")
        path = path.split("/")

        # Get the name
        length = len(path)
        parent = path[length - 2]

    return parent


def create_board_obj(root):   # for sequence, selector, and parallel nodes
    """ This function is responsible for recording objects to global memory"""
    tree_data = []

    # Traverse tree (pre-order)
    for node in PreOrderIter(root):
        name = node.name
        obj = Board()

        obj.name = name

        if "sequence" in name:
            obj.type = "sequence"
        elif "selector" in name:
            obj.type = "selector"
        elif "parallel" in name:
            obj.type = "parallel"

        # Record children
        if len(node.children) > 0:
            child_path = str(node.children).split(",")  # The path for the children of the selected node
            children = find_children(child_path)
            obj.children = copy.deepcopy(children)
        else:
            obj.children = 0

        # Record parent
        if node.parent is None:
            obj.parent = 'root'
        else:
            parent_node = str(node.parent).split(",")
            parent = find_parent(parent_node)
            obj.parent = parent

        if obj.type == "":
            obj.type = "leaf"

        if obj.name != "":  # Avoid recording empty nodes
            tree_data.append(obj)

    return tree_data


def tick_node(tree_data, node_name):
    """ Function to change the state of nodes to Success(True) when successful """

    for item in tree_data:
        if item.name == node_name:
            item.ticked = True

    return tree_data


def connect_node(tree_data, node_name, function):
    """ Function to connect action nodes with functions in code"""

    for item in tree_data:
        if item.name == node_name:
            item.action = function
    return tree_data


def lookup(tree_data, name):

    for item in tree_data:
        if item.name == name:  # node found

            if item.type == "selector":
                if item.ticked is False:
                    children = item.children
                    for i in range(0, len(children)):
                        if children[i] in nodes_ticked:
                            tree_data = tick_node(tree_data, item.name)
                            nodes_ticked.append(item.name)
                            break

            elif item.type == "sequence":
                running = False
                children = item.children

                for child_node in children:
                    if child_node not in nodes_ticked:
                        running = True

                if running is False:
                    tree_data = tick_node(tree_data, item.name)
                    nodes_ticked.append(item.name)
                    break

            elif item.type == "parallel":
                running = False
                children = item.children
                for child_node in children:
                    if child_node not in nodes_ticked:
                        running = True

                if running is False:
                    tree_data = tick_node(tree_data, item.name)
                    nodes_ticked.append(item.name)
                    break

    return tree_data


def lookup_parent_selector(tree_data, child):

    for item in tree_data:
        children = item.children
        if children != 0:
            if child in children:         # Parent found
                tree_data = tick_node(tree_data, item.name)
                nodes_ticked.append(item.name)
                break

    return tree_data


"""---------------------Functions to execute from action/leaf nodes-------------CAN modify----------------------"""

tracking_num = ""
validated = False
arrived = False


def prompt_tracking_num():
    user_input = input("Please enter your tracking number: ")

    if len(user_input) == 10:
        global tracking_num
        tracking_num = user_input

    return True


def tracking_num_available():
    global tracking_num
    if tracking_num != "":
        return True


def validate():
    global tracking_num
    global validated

    # Validation of user input
    valid_numbers = get_database_column(0)  # Tracking numbers
    if tracking_num in valid_numbers:
        validated = True
        print("Validation Successful!")
        print(" ")

        return True


def get_order_id(user_input):

    tracking_numbers = get_database_column(0)
    order_id = tracking_numbers.index(user_input)

    return order_id


def get_dispatch_date():
    global tracking_num
    global validated

    if arrived is False:
        if validated is True:
            dispatch_column = 2
            row = get_order_id(tracking_num)

            data = get_database_column(dispatch_column)
            date = data[row]
            print("Dispatch date: ", date)

            return True


def get_expected_arrival_date():
    global tracking_num
    global validated

    if arrived is False:
        if validated is True:
            arrival_column = 3
            row = get_order_id(tracking_num)

            data = get_database_column(arrival_column)
            date = data[row]
            print("Expected Arrival date: ", date)

            return True


def get_package_location():
    global tracking_num
    global validated

    if arrived is False:
        if validated is True:
            location_column = 4
            row = get_order_id(tracking_num)

            data = get_database_column(location_column)
            location = data[row]
            print("Package Location: ", location)

            return True


def get_package_destination():
    destination_column = 1
    row = get_order_id(tracking_num)

    data = get_database_column(destination_column)
    address = data[row]

    # print("Destination: ", address)

    return address


def package_arrived():
    global tracking_num
    global validated

    if validated is True:
        location_column = 4
        data = get_database_column(location_column)
        row = get_order_id(tracking_num)
        location = data[row]

        destination = get_package_destination()

        if location == destination:
            global arrived
            arrived = True
            print("Your package has arrived at ", destination)
            return True


"""--------------------------------------- DATA BASE -------------CAN change DB source ----------------------------"""


def get_database_column(column):

    # Change the database source, if using a database
    con = pymysql.connect(host="localhost", user="root", password="", database="delivery tracking")  # MySQL database
    data = []

    with con.cursor() as curs:
        # Get all items from ('packages') - chosen Table to work with
        curs.execute("SELECT * FROM `packages`")
        packages = curs.fetchall()
        # print(packages)

        # Get all tracking numbers - get specific items from the Table data
        num = len(packages)
        for i in range(0, num):
            item = packages[i][column]
            data.append(item)

    con.close()
    return data


"--------------------Attaching functions to leaf nodes---------The section below CAN be modified --------------------"


def big_traverse(tree_data):
    r = 0
    run = True
    while run is True:
        r += 1
        for current_node in tree_data:
            if current_node.ticked is True:
                if current_node.parent == "root":
                    nodes_ticked.append(current_node.name)
                    run = False
                    break  # cycle ended
                else:
                    continue
            else:
                #print("node ", current_node.name, " action: ", current_node.action)
                if len(current_node.action) > 3:
                    function = current_node.action
                    success = eval(function)

                    if success is True:
                        tree_data = tick_node(tree_data, current_node.name)
                        nodes_ticked.append(current_node.name)

                        parent = current_node.parent
                        if "selector" in parent:
                            tree_data = lookup_parent_selector(tree_data, current_node.name)
                else:
                    tree_data = lookup(tree_data, current_node.name)
                    print("current node:  ", current_node.name, len(current_node.name))

        if r >= 50:
            break

    for item in tree_data:
        print(item.name, item.type, item.parent, item.children, item.action, item.ticked)
    return tree_data


"""---------------------- Chat Bot -------------------Service Tag = "Tracking" --------- CAN modify Tag -----------"""


"""def run_bot(nodes, tree_data, root):
    intents = Bot.set_up_bot()

    bot_service = True
    while bot_service:

        user_input = input("You: ")
        Bot.write_to_file("User: " + user_input + "\n")
        user_input = Bot.strip_input(user_input).lower()

        if user_input == "quit":
            Bot.feedback(intents)
            break
        else:
            tag = Bot.find_tag(user_input, intents)

            if tag not in nodes:
                bot_service = Bot.activate_service(user_input, tag, intents)

                if bot_service == "Tracking":
                    Bot.write_to_file("Bot: Tracking...\n")
                    tree_data = big_traversing(nodes, tree_data, root, intents)
                    tree_data = tick_node(tree_data, tag)  # Tracking triggered
                    nodes_ticked.append(bot_service)
                    break

            if tag in nodes:
                Bot.write_to_file("Bot: Tracking...\n")
                tree_data = big_traversing(nodes, tree_data, root, intents)
                print(" ")
                tree_data = tick_node(tree_data, tag)  # Tracking triggered
                nodes_ticked.append(tag)
                break

    return tree_data
"""

"""------------------------- TK Inter for Displaying the flow of BT Model ---------------------------------------- """


def show_tree(root):           # MOVE
    graph = []
    # g = Graph()
    n1 = 0
    n2 = 0

    for pre, fill, node in RenderTree(root):  # Render tree
        # print("%s%s" % (pre, node.name))  # Display
        name = node.name

        if name == "sequence":
            n1 += 1
            name += str(n1)
        elif name == "selector":
            n2 += 1
            name += str(n2)

        g = "%s%s" % (pre, name)
        # g = node.name
        graph.append(g)

    # print(" ")
    return graph


def bt_window(graph):
    window = Tk()
    window.title("Behaviour Tree Model")
    window.geometry("560x420")
    window.config(background="#47383E")

    t = Text(window, height=15, width=35, font="Elephant")

    for x in graph:
        t.insert(END, x + '\n')
    t.pack(expand=True)

    window.mainloop()
    # return window


def progress_window(nodes):
    window = Tk()
    window.title("BT Execution")
    window.geometry("320x420")
    window.config(background="#47383E")

    t = Text(window, background="black")

    for item in nodes:  # for item in tree_data
        if item in nodes_ticked:
            label = Label(t, text=item, foreground="green", background="black", font="Elephant")
            label.pack()
        else:
            label = Label(t, text=item, foreground="red", background="black", font="Elephant")
            label.pack()

    t.pack(expand=True)
    # window.mainloop()
    return window


""" ------------------Main function for running tree-----------------do NOT modify-------------------------------- """


def generate_tree(file_name):
    # Get JSON String
    data = read_json(file_name)

    # Transform it into tree input
    tree = set_tree(data)

    # Create root data
    root_data = set_data(tree)

    # Index the repeating nodes
    root_data = index_nodes(root_data)

    # Create class instance
    root = eval(root_data)

    tree_data = create_board_obj(root)
    """for item in tree_data:
        print(item.name, item.type, item.parent, item.children)"""

    # Show BT model and progress in pop-up windows
    graph = show_tree(root)
    bt_window(graph)
    # progress = progress_window(nodes)
    # progress.mainloop()

    for item in tree_data:
        print(item.name, item.type, item.parent, item.children, item.action, item.ticked)

    return tree_data


#generate_tree('BTree.json')

