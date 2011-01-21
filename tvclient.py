#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib2
from hashlib import sha256

import simplejson
from PySide.QtCore import *
from PySide.QtGui import *

class MainForm(QDialog):
     
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.setWindowTitle('TimeVouch.com Client')
        
        self.formlayout = QFormLayout()

        filenamelayout = QHBoxLayout()
        self.filename = QLineEdit()
        self.filename.editingFinished.connect(self.calcdigest)
        filenamelayout.addWidget(self.filename, stretch=1)
        self.filedialogbutton = QPushButton('Select')
        self.filedialogbutton.clicked.connect(self.openfiledialog)
        filenamelayout.addWidget(self.filedialogbutton, stretch=0)

        self.formlayout.addRow('File', filenamelayout)

        self.digest = QLabel()
        self.digest.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.formlayout.addRow('Digest', self.digest)

        self.digestprogress = QProgressBar()
        self.digestprogress.setTextVisible(False)
        self.formlayout.addRow(self.digestprogress)

        self.secretword = QLineEdit('')
        self.formlayout.addRow('Secret word', self.secretword)

        self.testbutton = QPushButton('test')
        self.testbutton.clicked.connect(self.hashtest)
        self.formlayout.addRow(self.testbutton)
        
        self.sendbutton = QPushButton('Send to TimeVouch.com')
        self.sendbutton.clicked.connect(self.sendfile)
        self.sendbutton.setDisabled(True)
        self.formlayout.addRow(self.sendbutton)
        
        self.setLayout(self.formlayout)

    def hashtest(self):
        filename = "/usr/share/media/music/singles/Arlo Guthrie - Alice's Restaurant Massacree.mp3"
        self.filename.setText(filename)
        self.calcdigest()
        # self.calcdigest('/vmlinuz')
        # self.calcdigest('/home/kirk/.VirtualBox/HardDisks/Windows XP.vdi')
        # self.calcdigest('/home/kirk/.thunderbird/iklcxtsb.default/ImapMail/mail.daycos.com/INBOX.sbd/xrsnet')
        
    def passwordchanger(self):
        print 'passwordchange'

    def openfiledialog(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if not dialog.exec_():
            return
        filename = dialog.selectedFiles()[0]
        self.filename.setText(filename)
        self.calcdigest()

    def calcdigest(self):
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
        chunksize = 10 * 1024 * 1024
        self.digest.setText('Digesting...')
        while True:
            data = infile.read(chunksize)
            if not data:
                break
            totalread += len(data)
            self.digestprogress.setValue(totalread / progressdivisor)
            self.digestprogress.repaint()
            hasher.update(data)
        self.digest.setText(hasher.hexdigest())
        self.digestprogress.reset()
        self.sendbutton.setEnabled(True)

    def sendfile(self):
        postvars = {'docid': self.digest.text()}
        if self.secretword.text():
            postvars['secretword'] = self.secretword.text()
        data = urllib.urlencode(postvars)
        error = False
        try:
            request = urllib2.urlopen('http://timevouch.com/api', data)
        except urllib2.HTTPError, error:
            json = simplejson.loads(error.read())
            QMessageBox.warning(self, 'Error condition - %s' % json['error'], json['message'])
            return
        json = simplejson.loads(request.read())
        print json

        message = QMessageBox()
        olddoc = json['olddocid']
        if olddoc:
            message.setWindowTitle('TimeVouch.com results - verified registration')
            message.setText('This file has already been registered. Its contents have not been modified in any way since that time.')
        else:
            message.setWindowTitle('TimeVouch.com results - new registration')
            message.setText('This file had never been seen before, and has now been registered.')

        def maketr(key, value, style=None):
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
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = MainForm()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
