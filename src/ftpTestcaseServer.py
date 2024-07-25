import os
import ftpComm
dirpath = os.path.dirname(os.path.abspath(__file__))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    dir = os.path.join(dirpath, 'ftpServer_data')
    server = ftpComm.ftpServer(dir, port=8081, threadFlg=True)
    server.startServer()

if __name__ == "__main__":
    main()