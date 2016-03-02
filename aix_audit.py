#!/usr/local/bin/python2.7
import paramiko
import psycopg2

class bcolors:
    MAGENTA = '\033[95m'
    RED = '\033[93m'
    ENDC = '\033[0m'

def main():

    #Define our connection string
    conn_string = "host='TEMP' dbname='TEMP' user='TEMP' password='TEMP' connect_timeout=3"

    # print the connection string we will use to connect
    #print bcolors.MAGENTA + 'Connecting to database\n    ->%s' % (conn_string) + bcolors.ENDC + "\n"

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    sql = conn.cursor()
    print bcolors.RED + "Inserting AIX information into database.\n" + bcolors.ENDC

    #key = paramiko.RSAKey.from_private_key_file("./key")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #Begin SSH connection
    ssh.connect('TEMP', username='TEMP', password='TEMP')

    nodesp8 = ['TEMP','TEMP','TEMP','TEMP']

    for node in nodesp8:
        stdin, stdout, stderr = ssh.exec_command("lshwres -r proc -m %s --level lpar -F \"lpar_name curr_procs\"" % node)
        result = stdout.readlines()
        
        #Host and CPU number List remove \n
        cpuNum = [item.rstrip() for item in result]

        for line in result:
            (name,units) = line.split()
            units = int(units)
            ux40 = units - 1
            if ux40 != 0:
                print "%s %s UX40 %s" % (node, name, ux40)
                cmd = "INSERT INTO TEMP (device, host, ux, units) VALUES (%s, %s, %s, %s);"
                data = (node, name, "UX40", ux40,)
                sql.execute(cmd, data)

            print "%s %s UX20 %s" % (node, name, 1)
            cmd = "INSERT INTO TEMP (device, host, ux, units) VALUES (%s, %s, %s, %s);"
            data = (node, name, "UX20", 1,)
            sql.execute(cmd, data)

        stdin, stdout, stderr = ssh.exec_command("lshwres -r mem -m %s --level lpar -F \"lpar_name curr_mem\"" % node)
        result = stdout.readlines()
        
        #host and Memory usage List remove \n
        memNum = [item.rstrip() for item in result]

        for line in result:
            (name,units) = line.split()
            units = int(units)
            units = units / 1024
            ux30 = ((units - 2) / 2)
            print "%s %s UX30 %s" % (node, name, ux30)
            cmd = "INSERT INTO TEMP (device, host, ux, units) VALUES (%s, %s, %s, %s);"
            data = (node, name, "UX30", ux30,)
            sql.execute(cmd, data)

    conn.commit()
    sql.close()
    conn.close()
    
    #Close our SSH connection
    ssh.close()

if __name__ == "__main__":
    main()
