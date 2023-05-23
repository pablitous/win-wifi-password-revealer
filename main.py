import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk

if getattr(sys, 'frozen', False):
    execution_path = os.path.dirname(sys.executable)
    print(execution_path)
elif __file__:
    execution_path = sys.path[0]
    
#execution_path = sys.path[0]
xml_files = []  # Declare the xml_files list outside the if statement

def get_wifi_passwords():
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'export', 'profile', 'folder=' + execution_path, 'key=clear'], shell=True)
        output = output.decode('utf-8')  # Decode the byte string to a regular string
        return output
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with error code {e.returncode}")
        return None

def read_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return None

def extract_wifi_info(xml_root, show_passwords=False):
    namespace = get_namespace(xml_root)
    ssid = xml_root.find(f'.//{namespace}name').text
    authentication = xml_root.find(f'.//{namespace}authentication').text
    encryption = xml_root.find(f'.//{namespace}encryption').text
    if authentication == 'open':
        password = ''
    else:
        password = xml_root.find(f'.//{namespace}keyMaterial').text if show_passwords else '********'
    return ssid, authentication, encryption, password

def get_namespace(xml_root):
    # Extract the namespace from the XML root element
    # Assumes the first element has a namespace declaration
    namespace = xml_root.tag.split('}')[0][1:]
    return f'{{{namespace}}}'

def on_closing():
    for file in xml_files:
        os.remove(file)
    window.destroy()

wifi_passwords = get_wifi_passwords()

if wifi_passwords:
    def find_xml_files(folder_path):
        xml_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".xml"):
                    xml_files.append(os.path.join(root, file))
        return xml_files

    folder_path = execution_path  # Replace with the folder path you want to explore

    xml_files = find_xml_files(folder_path)

    if xml_files:
        def toggle_password_visibility():
            show_passwords = password_visibility.get()
            tree.delete(*tree.get_children())  # Clear existing tree items

            # Insert data into the Treeview with updated password visibility
            row_counter = 0
            for file in xml_files:
                root = read_xml_file(file)
                if root is not None:
                    ssid, authentication, encryption, password = extract_wifi_info(root, show_passwords)
                    row_counter += 1
                    tree.insert("", "end", text=str(row_counter), values=(ssid, authentication, encryption, password))
                else:
                    print("Failed to read XML file.")
                

        # Create a Tkinter window
        window = tk.Tk()
        window.iconbitmap(execution_path+"\\favicon.ico") 
        window.title("WiFi Information - By pablitous")
        window.protocol("WM_DELETE_WINDOW", on_closing)  # Call on_closing() when the window is closed

        # Create a Treeview widget
        tree = ttk.Treeview(window)
        tree["columns"] = ("SSID", "Authentication", "Encryption", "Password")
        tree.heading("#0", text="No.")
        tree.heading("SSID", text="WiFi Name")
        tree.heading("Authentication", text="Authentication")
        tree.heading("Encryption", text="Encryption")
        tree.heading("Password", text="Password")

        # Create a Checkbutton for toggling password visibility
        password_visibility = tk.BooleanVar()
        password_visibility.set(False)  # Passwords initially hidden
        password_checkbutton = ttk.Checkbutton(window, text="Show Passwords", variable=password_visibility, command=toggle_password_visibility)
        password_checkbutton.pack(padx=10, pady=(10, 0))

        # Insert data into the Treeview
        row_counter = 0
        for file in xml_files:
            root = read_xml_file(file)
            if root is not None:
                ssid, authentication, encryption, password = extract_wifi_info(root)
                row_counter += 1
                tree.insert("", "end", text=str(row_counter), values=(ssid, authentication, encryption, password))
            else:
                print("Failed to read XML file.")
            #os.remove(file)

        # Configure Treeview column widths
        tree.column("#0", width=40, anchor="center")
        tree.column("SSID", width=150)
        tree.column("Authentication", width=120)
        tree.column("Encryption", width=100)
        tree.column("Password", width=150)

        # Display the Treeview
        tree.pack(padx=10, pady=10)

        # Start the Tkinter event loop
        window.mainloop()
    else:
        print("No XML files found in the folder.")
else:
    print("Failed to retrieve Wi-Fi passwords.")
