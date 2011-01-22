#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Functions and a GUI for registering and verifying files with the
TimeVouch.time free public timestamping service"""

import os
import sys
import urllib
import urllib2
from hashlib import sha256

import simplejson
from PySide import QtCore
from PySide import QtGui

TIMEVOUCHURL = 'https://timevouch.com/api'
DIGESTCHUNKSIZE = 10 * 1024 * 1024

def sendfiletotimevouch(digest, secretword):
    """Send the digest and secretword to TimeVouch.com. Returns either
    True or False to indicate success, and a dict of keys and values
    returned by the service"""
    postvars = {'docid': digest}
    if secretword:
        postvars['secretword'] = secretword
    data = urllib.urlencode(postvars)
    try:
        request = urllib2.urlopen(TIMEVOUCHURL, data)
    except urllib2.HTTPError, error:
        return False, simplejson.loads(error.read())
    return True, simplejson.loads(request.read())

class MainForm(QtGui.QDialog):
    """Give users a GUI to easily interact with the TimeVouch.com
    timestamping service"""
     
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.setWindowTitle('TimeVouch.com Client')
        
        self.formlayout = QtGui.QFormLayout()

        # Use a horizontal layout to put the 'Select' button right
        # after the filename text field
        filenamelayout = QtGui.QHBoxLayout()
        self.filename = QtGui.QLineEdit()
        self.filename.editingFinished.connect(self.calcdigest)
        filenamelayout.addWidget(self.filename, stretch=1)

        self.filedialogbutton = QtGui.QPushButton('Select')
        self.filedialogbutton.clicked.connect(self.getanddigestfile)
        # This button is clickable, but don't bounce to it with the
        # keyboard
        self.filedialogbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        filenamelayout.addWidget(self.filedialogbutton, stretch=0)

        self.formlayout.addRow('File', filenamelayout)

        # This label gets update with the digest after we calculate it
        self.digest = QtGui.QLabel()
        self.digest.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.formlayout.addRow('Digest', self.digest)

        # This shows the progress of very long calculations
        self.digestprogress = QtGui.QProgressBar()
        self.digestprogress.setTextVisible(False)
        self.formlayout.addRow(self.digestprogress)

        # Enter secret words here
        self.secretword = QtGui.QLineEdit('')
        self.formlayout.addRow('Secret word', self.secretword)

        if False:
            self.testbutton = QtGui.QPushButton('test')
            self.testbutton.clicked.connect(self.hashtest)
            self.formlayout.addRow(self.testbutton)

        # Handle the registration process
        self.sendbutton = QtGui.QPushButton('Send the digest to TimeVouch.com')
        self.sendbutton.clicked.connect(self.sendfile)
        self.sendbutton.setDisabled(True)
        self.formlayout.addRow(self.sendbutton)
        
        self.setLayout(self.formlayout)
        self.setMinimumWidth(640)

    # def hashtest(self):
    #     """Useful for debugging"""
    #     filename = "/usr/share/media/music/singles/Arlo Guthrie - Alice's Restaurant Massacree.mp3"
    #     self.filename.setText(filename)
    #     self.calcdigest()
    #     # self.calcdigest('/vmlinuz')
    #     # self.calcdigest('/home/kirk/.VirtualBox/HardDisks/Windows XP.vdi')
    #     # self.calcdigest('/home/kirk/.thunderbird/iklcxtsb.default/ImapMail/mail.daycos.com/INBOX.sbd/xrsnet')
        
    def calcdigest(self):
        """Calculate the SHA-256 digest of the file whose name is in
        the self.filename widget"""
        hasher = sha256()
        filename = self.filename.text()
        if not filename:
            return
        if filename.startswith('file://'):
            filename = filename[7:]
        self.digest.clear()
        self.sendbutton.setDisabled(True)
        progressdivisor = float(os.path.getsize(filename)) / 100
        infile = open(filename)
        totalread = 0
        self.digest.setText('Digesting...')
        while True:
            data = infile.read(DIGESTCHUNKSIZE)
            if not data:
                break
            totalread += len(data)
            self.digestprogress.setValue(totalread / progressdivisor)
            self.digestprogress.repaint()
            hasher.update(data)
        self.digest.setText(hasher.hexdigest())
        self.digestprogress.reset()
        self.sendbutton.setEnabled(True)

    def getanddigestfile(self):
        """Allow the user to select a file, then calculate its
        digest"""
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        if not dialog.exec_():
            return
        filename = dialog.selectedFiles()[0]
        self.filename.setText(filename)
        self.calcdigest()

    def sendfile(self):
        """Send the digest (and possibly secret word) to the
        TimeVouch.com server and display the results"""

        success, json = sendfiletotimevouch(self.digest.text(), self.secretword.text())
        if not success:
            QtGui.QMessageBox.warning(self, 'Error condition - %s' % json['error'], json['message'])
            return
        
        message = QtGui.QMessageBox()
        olddoc = json['olddocid']
        if olddoc:
            message.setWindowTitle('TimeVouch.com results - verified registration')
            message.setText('This file has already been registered. Its contents have not been modified in any way since that time.')
        else:
            message.setWindowTitle('TimeVouch.com results - new registration')
            message.setText('This file had never been seen before, and has now been registered.')

        def maketr(key, value, style=None):
            """Turn the given key, value, and optional CSS style into
            a table row"""
            if style:
                stylestr = ' style="%s"' % style
            else:
                stylestr = ''
            key = key.replace(' ', '&nbsp;')
            return '<tr><td>%s</td><td%s>%s</td></tr>' % (key, stylestr, value)

        lines = []
        lines.append(maketr('Document ID:', json['docid'], 'color: blue;'))
        lines.append(maketr('Registered:', json['registered'], 'color: green;'))
        lines.append(maketr('Current time:', json['currenttime'], 'color: green;'))
        if olddoc:
            validatesummarycolor = {'unavailable' : 'blue',
                                    'successful'  : 'green',
                                    'unsuccessful': 'red',}[json['validatesummary']]
            lines.append(maketr('Extended validation:', json['validatesummary'], 'color: %s;' % validatesummarycolor))
        text = '<table>' + '\n'.join(lines) + '</table>'
        if olddoc:
            text += '<p>%s</p>' % json['validatemessage']
        message.setInformativeText(text)
        message.setDetailedText(str(json))
        message.exec_()
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    form = MainForm()
    form.show()
    sys.exit(app.exec_())
