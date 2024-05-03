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

cred_names = {
    "Sign in to Steam": "steam",
    "Epic Games Launcher": "epic"
}
    
def single_window_login(username, password):
    time.sleep(0.5)
    keyboard.write(username)
    keyboard.send('tab', do_press=True, do_release=True)
    time.sleep(0.5)
    keyboard.write(password)
    keyboard.send('enter', do_press=True, do_release=True)
    
space_hook_id=0

def on_space_press(password):
    global space_hook_id
    def callback(event):
        keyboard.send('tab', do_press=True, do_release=True)
        keyboard.send('tab', do_press=True, do_release=True)
        keyboard.write(password)
        keyboard.send('enter', do_press=True, do_release=True)
        keyboard.unhook(space_hook_id)
    return callback

def two_window_login(username, password):
    global space_hook_id

    try:
        keyboard.unhook(space_hook_id)
    except Exception as e:
        print("This is just incase a fool spams it: ", e)

    time.sleep(0.5)
    keyboard.write(username)
    keyboard.send('enter', do_press=True, do_release=True)

    # Register the partial function as the callback
    space_hook_id = keyboard.on_press_key('space', on_space_press(password))

cred_login_files = {
    "steam": single_window_login,
    "epic": two_window_login
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
def username():
    print(sys.argv[2])
    if sys.argv[2] is not None:
        #return sys.argv[0]
        pass
    # u = getpass.getuser().lower().strip().replace('.', '_')
    u = socket.gethostname().lower().strip().replace('.', '_')
    # print(u)
    return u

# Setup a first time user
def setup_user():
    # Send HTTP GET request to your server
    response = requests.get(f'http://localhost:3001/user/{username()}')
    # Get the response text
    output = response.text
    return output

# Get a users credential
def get_credential(credential):
    if credential is None: return None
    # Send HTTP GET request to your server
    response = requests.get(f'http://localhost:3001/credential/{username()}/{credential}')
    # Get the response text
    output = response.text
    return output

# Set a users credential
def set_credential(credential, user, pw):
    if credential is None: return None
    # Prepping the payload!
    data = {
        'username': user,
        'password': pw
    }
    # Send HTTP GET request to your server
    response = requests.post(f'http://localhost:3001/credential/{username()}/{credential}', json=data)
    # Get the response text
    output = response.text
    return output

# Delete a users credential
def del_credential(credential):
    if credential is None: return None
    # Send HTTP GET request to your server
    response = requests.delete(f'http://localhost:3001/credential/{username()}/{credential}')
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

# Setup a user
def do_setup():
    if is_admin():
        output = setup_user()
        if output is None: return None
        print_window(output)
    else:
        print_window("You need to run this as an admin to setup users.")

# When we are executed directly
def main():
    # Define the key combinations
    login_cb = 'ctrl+alt+l'
    remove_login_cb = 'ctrl+alt+r'
    add_login_cb = 'ctrl+alt+s'
    first_time_cb = 'ctrl+alt+u'
    end_cb = 'ctrl+alt+e'
    print("Press {} to login.".format(login_cb))
    
    # Start listening for the key combinations
    keyboard.add_hotkey(login_cb, do_login)
    keyboard.add_hotkey(remove_login_cb, remove_login)
    keyboard.add_hotkey(add_login_cb, set_login)
    keyboard.add_hotkey(first_time_cb, do_setup)

    # Keep the script running
    keyboard.wait(end_cb)  # Press the combination to exit the script

if __name__ == "__main__":
    main()