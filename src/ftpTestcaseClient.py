import os
import ftpComm
dirpath = os.path.dirname(os.path.abspath(__file__))

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    dir = os.path.join(dirpath, 'ftpClient_data')
    client = ftpComm.ftpClient('127.0.0.1', 8081, 'admin', '123456')
    client.connectToServer()

    print("test create folder")
    try:
        rst = client.swithToDir('client1')
    except Exception as erro:
        client.createDir('client1')
        client.swithToDir('client1')
    print("test upload file")
    print(client.listDirInfo())
    print(client.listDirInfo(detail=True))
    localFile = os.path.join(dir,'109474714_S7300_ModbusRTU_TIA_DOC_v30_en.pdf')
    client.uploadFile(localFile, 'uploadfile.pdf')
    print("test downloadfile")
    client.swithToDir('/')
    downloadfilepath = os.path.join(dir, 'downloadfile.pdf')
    client.downloadFile('Hacking - NMap Quick Reference Guide.pdf', downloadfilepath)


if __name__ == "__main__":
    main()