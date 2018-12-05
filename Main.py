import socket
from thread import *
import threading
import datetime 
import mysql.connector
from API import *
from Database import *
HOST = '0.0.0.0'
PORT = 23
#Password for administrative Prompt. Implement bycrpt
PASSWORD = "password"
#Lock for adding to Database
Add_lock = threading.Lock()


#Closes connection, Simple.
def ClientClose(c):
    c.send("Closing Connection\0")
    c.close()
    Add_lock.release()
    return

#Prompt for administrative CLI
def Prompt(c):
    c.send("> ")
    return (c.recv(1024)).rstrip("\r\n")


# Prints Connections to admin prompt
def PrintConns(client, command, __DB_OP):
        i = 0
        for OP in command:
            i = i + 1
            #If specific device id is selected by admin
            if OP == "-s":
                #print OP
                #print command
                Device = __DB_OP.SelectItemByID(command[i])
                #print Device
                break
            else:
                #Select All if not
                Device = __DB_OP.SelectAll()
        i = 0
        for PC in Device: #For each PC in the Device tuple returned by Datbase, print info
                 i = i + 1
                 client.send("Device " + str(PC[0]) + "\n")
                 client.send("     Connection Address: " + PC[1] + "\n")
                 client.send("     Device Info: " + PC[2] + "\n")
                 client.send("     Host Name: " + PC[3] + "\n")
                 client.send("     Time of Last Connection: " + PC[4] + "\n")
        return
                                                                





def AdminMenu(command):
    if command[0] == "help":
        return " help - Return Help Menu \n exit - End Connection\n show - Show all devices logged\n del - Delete Device\n"
    if command[0] == "show":
        return 2
    if command[0] == "del":
        return 3

    return " "


def DeleteDevice(c, command, __DB_OP):
    __DB_OP.DeleteDevice(command[1])
    c.send("Deleted Device "
           + str(command[1])
           + "\n")
    return



def AdministrativeCLI(c, __DB_OP):
    c.send("Administrative CLI for Serv CLient\n\0")
    c.send("Password: ");
    data = (c.recv(1024)).rstrip("\r\n")
    if data != PASSWORD:
        c.send("Invalid Pass! \n Disconnecting!\n")
        c.close()
        return
    c.send("Password Accepted\n")
    command = [None,] 
    while command[0] != "exit":
        command = Prompt(c)
        command = command.split(" ")
        menuop = AdminMenu(command)
        if menuop == 2:
            PrintConns(c, command,__DB_OP)
        elif menuop == 3:
            DeleteDevice(c, command,__DB_OP)
        else:
            c.send(menuop)
    c.send("Exiting!\n")
    c.close()
    return
    
def ClientAdd(c, addr, db):
    #__DB_OP is the database operation class. Wraps all database operations into a single module 
    __DB_OP = DatabaseOperation(db)
    c.send("ConnectionTest\0")
    data = c.recv(1024)
    #REMOVE FOUND! ITS NOT USED!
    found = 0
    if data.rstrip("\n\r") == "<API>":
        API(c, db) #Need to change API to use Database module
        Add_lock.release()
        return
    
    if data.rstrip("\n\r") == "AdminMenu":
        Add_lock.release()
        AdministrativeCLI(c, __DB_OP)
        return
    #Search for device hostname in Database
    DeviceFinal = __DB_OP.SelectItemByHostname(data.rstrip("\r\n"))
    #If device is not found, move onto creating device
    if DeviceFinal == None:
        i = 1
    else:
        #Update old device with new time
        __DB_OP.UpdateDevice(DeviceFinal[0])
        c.send("Update\0")
        ClientClose(c)
        return
        
    if found == 0:
        c.send("Info\0")
        data = c.recv(1024)
        #Splits data from client into list. Systeminfo [ System Hostname
        #Checks to makesure data is formatted correctly 
	if "[" in data:
                data = data.split("[")
                #Insert new device into database
                __DB_OP.AddDevice((addr[0], data[0], data[1], str(datetime.datetime.now())))
        	c.send("Added\0")
        	ClientClose(c)
        	return
	else:
		print "Device sent malformed data!\n"
		c.send("Homie u messed up!\0")
		ClientClose(c)
                return
    Add_lock.release()
    return


#Bind to port and start listening
def SocketSetup():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(5)
    return s

def main():

        database = DatabaseOpen()
        db = database.DatabaseINIT()
        s = SocketSetup()
        while True:
            client, address = s.accept()
            Add_lock.acquire()
            start_new_thread(ClientAdd, (client, address, db))
        s.close()







if  __name__=="__main__":
	main()
