#!/usr/bin/env python
# combine_allin1.py - combination of ShowGPL, About, Close scripts
# The purpose of this version of program is to show implementation 
# of most code in one file - all_in_1!.
 
#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson
import sys
import urllib
import urllib2
from hashlib import sha256

from PySide.QtCore import *
from PySide.QtGui import *
 
class Form(QDialog):
     
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        formlayout = QFormLayout()
        self.filebutton = QPushButton("Select the file to register or verify")
        self.filenamelabel = QLabel()
        self.filenamelabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.digestlabel = QLabel(' ' * 80)
        self.digestlabel.setText('')
        self.digestlabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.secretword = QLineEdit()
        self.sendbutton = QPushButton('Send to TimeVouch.com')
        self.sendbutton.setDisabled(True)
        formlayout.addRow(self.filebutton)
        formlayout.addRow('File:', self.filenamelabel)
        formlayout.addRow('Hash value:', self.digestlabel)
        formlayout.addRow('Secret word:', self.secretword)
        formlayout.addRow(self.sendbutton)

        self.setLayout(formlayout)

        # Add button signal to greetings slot
        self.filebutton.clicked.connect(self.selectfile)
        self.secretword.textChanged.connect(self.handlesecretword)
        self.sendbutton.clicked.connect(self.sendfile)
         
    # Greets the user
    def handlesecretword(self):
        if self.secretword.text():
            if self.digestlabel.text():
                self.sendbutton.setEnabled(True)
        else:
            self.sendbutton.setDisabled(True)
 
    def selectfile(self):
        filename, filefilter = QFileDialog.getOpenFileName(self, 'File to register or verify')
        self.filenamelabel.setText(filename)
        if filename:
            hasher = sha256()
            with open(filename) as infile:
                while True:
                    chunk = infile.read(1024 * 1024)
                    if not chunk:
                        break
                    hasher.update(chunk)
            self.digestlabel.setText(hasher.hexdigest())
            if self.secretword.text():
                self.sendbutton.setEnabled(True)
        else:
            self.digestlabel.setText('')
            self.sendbutton.setDisabled(True)

    def sendfile(self):
        data = urllib.urlencode({'docid'     : self.digestlabel.text(),
                                 'secretword': self.secretword.text(),})
        post = urllib2.urlopen('http://timevouch.com/api', data)
        result = simplejson.loads(post.read())
        print result
        
if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())

# print QFileDialog.getOpenFileName(self, 'Species Explorer - Open Species', dir, 'Species Files (*.species)')
 
