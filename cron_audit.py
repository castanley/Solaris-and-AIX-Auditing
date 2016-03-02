#!/usr/local/bin/python2.7
import psycopg2
import sun_audit
import aix_audit

class bcolors:
    MAGENTA = '\033[95m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def main():

    #Define our connection string
    conn_string = "host='TEMP' dbname='TEMP' user='TEMP' password='TEMP' connect_timeout=3"

    # print the connection string we will use to connect
    print bcolors.MAGENTA + 'Connecting to database\n    ->%s' % (conn_string) + bcolors.ENDC + "\n"

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    sql = conn.cursor()
    print bcolors.RED + "Dumping database: 'DELETE FROM TEMP;' \n" + bcolors.ENDC

    sql.execute('DELETE FROM TEMP;')

    conn.commit()
    sql.close()
    conn.close()

    sun_audit.main()
    aix_audit.main()

    print bcolors.GREEN + "Great Success!\n" + bcolors.ENDC

if __name__ == "__main__":
    main()
