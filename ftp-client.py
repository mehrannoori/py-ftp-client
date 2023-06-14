#!/bin/env python

import os, sys, ftplib
from getpass import getpass
from mimetypes import guess_type, add_type

dfltSite = 'ftpupload.net'
dfltRdir = 'htdocs'
dfltUser = 'b12_34150225'

class FtpTools:
    def get_localdir(self):
        return (len(sys.argv)>1 and sys.argv[1]) or '.'
    
    def get_cleanall(self):
        return input('Clean target dir first? ')[:1] in ['y', 'Y']

    def getpassword(self):
        return getpass(
            'Password for %s in %s'%(self.remoteuser, self.remotesite))

    def configTransfer(self,site=dfltSite, rdir=dfltRdir, user=dfltUser):
        self.nonepassive = False
        self.remotesite = site
        self.remotedir = rdir
        self.remoteuser = user
        self.localdir = self.get_localdir()
        self.cleanall = self.get_cleanall()
        self.remotepass = self.getpassword()

    def isTextKind(self, remotename, trace=True):
        add_type('text/x-python-win', 'pyw')
        mimetype, encoding = guess_type(remotename, strict=False)
        mimetype = mimetype or '?/?'
        maintype = mimetype.split('/')[0]
        if trace: print(maintype, encoding or '')
        return maintype == 'text' and encoding == None

    def connectFtp(self):
        print('Connecting...')
        connection = ftplib.FTP(self.remotesite)
        connection.login(self.remoteuser, self.remotepass)
        connection.cwd(self.remotedir)
        if self.nonepassive:
            connection.set_pasv(False)
        self.connection = connection
    
    def cleanLocals(self):
        if self.cleanall:
            for localname in os.listdir(self.localdir):
                try:
                    print("delete local", localname)
                    os.remove(os.path.join(self.localdir, localname))
                except:
                    print('cannot delete', localname)
    
    def cleanRemotes(self):
        if self.cleanall:
            for remotename in self.connection.nlst():
                try:
                    print('delete remote', remotename)
                    self.connection.delete(remotename)
                except:
                    print('cannot delete', remotename)

    def downloadOne(self, remotename, localpath):
        if self.isTextKind(remotename):
            localfile = open(localpath, 'w', encoding=self.connection.encoding)
            def callback(line): localfile.write(line+'\n')
            self.connection.retrlines('RETR '+remotename, callable)
        else:
            localfile = open(localpath, 'wb')
            self.connection.retrbinary('RETR '+remotename, localfile.write)
        localfile.close()

    def uploadOne(self, localname, localpath, remotename):
        if self.isTextKind(remotename):
            localfile = open(localpath, 'rb')
            self.connection.storlines('STOR '+remotename, localfile)
        else:
            localfile = open(localpath, 'rb')
            self.connection.storbinary('STOR '+remotename, localfile)
        localfile.close()

    def downloadDir(self):
        remotefiles = self.connection.nlst()
        for remotename in remotefiles:
            if remotename in ['.', '..']: continue
            localpath = os.path.join(self.localdir, remotename)
            print('downloading', remotename, 'to', localpath)
            self.downloadOne(remotename, localpath)
        print('Done:', len(remotefiles), 'files downloaded.')

    def uploadDir(self):
        localfiles = os.listdir(self.localdir)
        for localname in localfiles:
            localpath = os.path.join(self.localdir, localname)
            print('uploading', localpath, 'to', localname)
            self.uploadOne(localname, localpath, localname)
        print('Done:', len(localfiles), 'files uploaded.')

    def run(self, cleanTarget=lambda:None, transferAct=lambda:None):
        self.connectFtp()
        cleanTarget()
        transferAct()
        self.connection.quit()

if __name__ == '__main__':
    ftp = FtpTools()
    xfermode = 'download'
    if len(sys.argv) > 1:
        xfermode = sys.argv.pop(1)
    if xfermode == 'download':
        ftp.configTransfer()
        ftp.run(cleanTarget=ftp.cleanLocals, transferAct=ftp.downloadDir)
    elif xfermode == 'upload':
        ftp.configTransfer(site=dfltSite, rdir=dfltRdir, user=dfltUser)
        ftp.run(cleanTarget=ftp.cleanRemotes, transferAct=ftp.uploadDir)
    else:
        print('Usage: ftptools.py ["download" | "upload"] [localdir]')                