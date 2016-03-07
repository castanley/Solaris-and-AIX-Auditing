#!/usr/local/bin/python2.7
import sys, os, string, threading
import paramiko
import psycopg2

#paramiko.util.log_to_file("sun_audit.log")

getCPU = "/usr/sbin/psrinfo -p"
getMEM = "/usr/sbin/prtconf | grep \"Memory\" | awk '{ print $3 }'"
getHOST = "hostname"

class bcolors:
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'

def workon(host,sql):

    #Connect to each host
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey.from_private_key_file("./cstanley")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='cstanley', pkey=key)

    #Run Commands
    stdinHOST, stdoutHOST, stderrHOST = ssh.exec_command(getHOST)
    stdinCPU, stdoutCPU, stderrCPU = ssh.exec_command(getCPU)
    stdinMEM, stdoutMEM, stderrMEM = ssh.exec_command(getMEM)

    with threading.Lock():
        resultHOST = stdoutHOST.readlines()
        print "{0} {0} UX10 1".format(resultHOST[0].rstrip())
        cmd = "INSERT INTO TEMP (device, host, ux, units) VALUES (%s, %s, %s, %s);"
        data = ("solaris-cdc", resultHOST[0], "UX10", 1,)
        sql.execute(cmd, data)

        resultCPU = stdoutCPU.readlines()
        ux40 = (int(resultCPU[0].rstrip()) - 1)
        if ux40 != 0:
            print "{0} {0} UX40 {1}".format(resultHOST[0].rstrip(),ux40)
            cmd = "INSERT INTO cstanley_temp (device, host, ux, units) VALUES (%s, %s, %s, %s);"
            data = ("solaris-cdc", resultHOST[0], "UX40", ux40,)
            sql.execute(cmd, data)

        resultMEM = stdoutMEM.readlines()
        ux30 = (int(resultMEM[0].rstrip()) / 1024 - 2) / 2
        print "{0} {0} UX30 {1}".format(resultHOST[0].rstrip(),ux30)
        cmd = "INSERT INTO TEMP (device, host, ux, units) VALUES (%s, %s, %s, %s);"
        data = ("solaris-cdc", resultHOST[0], "UX30", ux30,)
        sql.execute(cmd, data)

        ssh.close()

def main():

    #Define our connection string
    conn_string = "host='TEMP' dbname='TEMP' user='TEMP' password='TEMP' connect_timeout=3"

    # print the connection string we will use to connect
    print bcolors.MAGENTA + 'Connecting to database\n    ->%s' % (conn_string) + bcolors.ENDC + "\n"

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    sql = conn.cursor()
    print bcolors.YELLOW + "Inserting Solaris information into table.\n" + bcolors.ENDC

    with open('./sun_ip') as ip:
        hosts = ip.read().splitlines()

    threads = []
    for h in hosts:
        t = threading.Thread(target=workon, args=(h,sql,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    conn.commit()
    sql.close()
    conn.close()

if __name__ == "__main__":
    main()
