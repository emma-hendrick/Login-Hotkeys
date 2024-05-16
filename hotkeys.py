import keyboard
import requests
import time
import json
import socket
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import ctypes
import pygetwindow as gw
import sys
import os

# Credential short names
cred_names = {
    "Sign in to Steam": "steam",
    "Epic Games Launcher": "epic",
    "Sign in - Google Accounts - Google Chrome": "google",
    "EA": "ea",
    "Ubisoft Connect": "ubisoft",
    "Login - Spotify - Google Chrome": "spotify"
}

# Whether to associate a credential with a user or the computer
# For this true will represent user, false will represent computer
use_user = {
    "steam": False,
    "epic": False,
    "google": True,
    "ea": False,
    "ubisoft": False,
    "spotify": True
}
    
def single_window_login(username, password):
    time.sleep(0.5)
    keyboard.write(username)
    keyboard.send('tab', do_press=True, do_release=True)
    time.sleep(0.5)
    keyboard.write(password)
    keyboard.send('enter', do_press=True, do_release=True)
    
space_hook_id=0

def on_space_press_tabbed(password):
    global space_hook_id
    def callback(event):
        keyboard.send('tab', do_press=True, do_release=True)
        keyboard.send('tab', do_press=True, do_release=True)
        keyboard.write(password)
        keyboard.send('enter', do_press=True, do_release=True)
        keyboard.unhook(space_hook_id)
    return callback

def on_space_press_tabless(password):
    global space_hook_id
    def callback(event):
        keyboard.write(password)
        keyboard.send('enter', do_press=True, do_release=True)
        keyboard.unhook(space_hook_id)
    return callback

def two_window_epic_login(username, password):
    global space_hook_id

    try:
        keyboard.unhook(space_hook_id)
    except Exception as e:
        print("This is just incase a fool spams it: ", e)

    time.sleep(0.5)
    keyboard.write(username)
    keyboard.send('enter', do_press=True, do_release=True)

    # Register the partial function as the callback
    space_hook_id = keyboard.on_press_key('space', on_space_press_tabbed(password))

def two_window_standard_login(username, password):
    global space_hook_id

    try:
        keyboard.unhook(space_hook_id)
    except Exception as e:
        print("This is just incase a fool spams it: ", e)

    time.sleep(0.5)
    keyboard.write(username)
    keyboard.send('enter', do_press=True, do_release=True)

    # Register the partial function as the callback
    space_hook_id = keyboard.on_press_key('space', on_space_press_tabless(password))

cred_login_files = {
    "steam": single_window_login,
    "epic": two_window_epic_login,
    "google": two_window_standard_login,
    "ea": single_window_login,
    "ubisoft": single_window_login,
    "spotify": single_window_login
}

# For restricted actions
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# A window to get user input
def prompt_window(prompt_text):
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    user_input = simpledialog.askstring("Input", prompt_text)
    root.destroy()  # Destroy the root window after obtaining the input

    return user_input

# A window to output to the user
def print_window(output_text):
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    messagebox.showinfo("Output", output_text)

    root.destroy()  # Destroy the root window after displaying the output

# Get the current users username
def username(isUser=False):
    if isUser:
        if len(sys.argv) > 1 and sys.argv[1] is not None:
            # User specified
            return sys.argv[1]
        else:
            # Default user
            # u = getpass.getuser().lower().strip().replace('.', '_')
            u = os.getlogin()
            return u
    else:
        # Get the computers name
        if  len(sys.argv) > 2 and sys.argv[2] is not None:
            # Computer specified
            return sys.argv[2]
        else:
            # Default computerwide user
            # u = getpass.getuser().lower().strip().replace('.', '_')
            u = socket.gethostname().lower().strip().replace('.', '_')
            # print(u)
            return u
    
# Setup a first time user
def setup_user(asUser=False):
    # Send HTTP GET request to your server
    response = requests.get(f'http://localhost:3001/user/{username(asUser)}')
    # Get the response text
    output = response.text
    return output

# Get a users credential
def get_credential(credential):
    if credential is None: return None
    asUser = use_user[credential]
    # Send HTTP GET request to your server
    response = requests.get(f'http://localhost:3001/credential/{username(asUser)}/{credential}')
    # Get the response text
    output = response.text
    return output

# Set a users credential
def set_credential(credential, user, pw):
    if credential is None: return None
    asUser = use_user[credential]
    # Prepping the payload!
    data = {
        'username': user,
        'password': pw
    }
    # Send HTTP GET request to your server
    response = requests.post(f'http://localhost:3001/credential/{username(asUser)}/{credential}', json=data)
    # Get the response text
    output = response.text
    return output

# Delete a users credential
def del_credential(credential):
    if credential is None: return None
    asUser = use_user[credential]
    # Send HTTP GET request to your server
    response = requests.delete(f'http://localhost:3001/credential/{username(asUser)}/{credential}')
    # Get the response text
    output = response.text
    return output

# Get the login target of the active window
def get_credential_needed():
    active_window = gw.getActiveWindow()
    if active_window is not None:
        print("Logging on to window: ", active_window.title)
        if active_window.title in cred_names: 
            return cred_names[active_window.title]
        return None
    else:
        print_window('You must have an active window to login')
        return None

# Log in to the correct thing
def do_login():
    cred_name = get_credential_needed()
    output = get_credential(cred_name)
    if output is None: return None

    try:
        credential = json.loads(output)
    except Exception as e:
        print("An error has occured:", e)
        return
    
    cred_login_files[cred_name](credential['username'], credential['password'])

# Remove a login
def remove_login():
    if is_admin():
        output = del_credential(get_credential_needed())
        if output is None: return None
        print_window(output)
    else:
        print_window("You need to run this as an admin to remove logins.")

# Set a login
def set_login():
    if is_admin():
        username = prompt_window("What is your username? ")
        password = prompt_window("What is your password? ")
        output = set_credential(get_credential_needed(), username, password)
        if output is None: return None
        print_window(output)
    else:
        print_window("You need to run this as an admin to add logins.")

# Setup a computer
def do_setup():
    if is_admin():
        output = setup_user()
        if output is None: return None
        print_window(output)
    else:
        print_window("You need to run this as an admin to setup users.")

# Setup a user
def do_setup_user():
    output = setup_user(True)
    if output is None: return None
    print_window(output)

# When we are executed directly
def main():
    # Define the key combinations
    login_cb = 'ctrl+alt+l'
    remove_login_cb = 'ctrl+alt+r'
    add_login_cb = 'ctrl+alt+s'
    first_time_cp_cb = 'ctrl+alt+c'
    first_time_us_cb = 'ctrl+alt+u'
    end_cb = 'ctrl+alt+e'
    print("Press {} to login.".format(login_cb))
    
    # Start listening for the key combinations
    keyboard.add_hotkey(login_cb, do_login)
    keyboard.add_hotkey(remove_login_cb, remove_login)
    keyboard.add_hotkey(add_login_cb, set_login)
    keyboard.add_hotkey(first_time_cp_cb, do_setup)
    keyboard.add_hotkey(first_time_us_cb, do_setup_user)

    # Keep the script running
    keyboard.wait(end_cb)  # Press the combination to exit the script

if __name__ == "__main__":
    main()