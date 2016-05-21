import requests
from json import dumps as json
import getpass

__author__ = "JiaJiunn Chiou"
__license__= ""
__version__= "0.0.1"
__status__ = "Prototype"

class PyiCloud:
    def __init__ (self):
        self.urlBase = "https://www.icloud.com/"
        self.urlAuth = "https://idmsa.apple.com"
        self.urlSignIn = self.urlAuth + "/appleauth/auth/signin"#?widgetKey="
        self.urlKey = "https://setup.icloud.com/setup/ws/1/validate"
        self.mailBase = "@icloud.com"
        self.appleWidgetKey = None

        self.session = requests.Session()
        self.response = None
        self.accountName = None
        self.userAgent = "Python (X11; Linux x86_64)" 

    def getAuthenticationRequestPayload (self, password):
        return json({
                "accountName": self.accountName,
                "password": password,
                "rememberMe": False
                }) 

    def getAuthenticationRequestHeader (self):
        return {
                "Accept": "application/json, text/javascript",
                "Content-Type": "application/json",
                "User-Agent": self.userAgent,
                "X-Apple-Widget-Key": self.appleWidgetKey,
                "X-Requested-With": "XMLHttpRequest"
                }

class iCloudWidgets:
    mail = "mail"
    contacts = "contacts"
    calendar = "calendar"
    photos = "photos"
    iCloudDrive = "iclouddrive"
    notes = "notes"
    reminders = "reminders"
    pages = "pages"
    numbers = "numbers"
    keynote = "keynote"
    findFriends = "findFriends"
    findiPhone = "findiphone"
    settings = "settings"

class PyiCloudService (PyiCloud):
    def __init__ (self):
        super(PyiCloudService, self).__init__()
        self._ESCAPE_CHAR = ",;&%!?|(){}[]~>*\'\"\\"

    def requestAppleWidgetKey (self):
        #self.urlBase + "/system/cloudos/16CHotfix21/en-us/javascript-packed.js"
        self.response = self.session.get(self.urlKey)
        #self.checkStatusCode() #TODO: this fails
        try:
            self.appleWidgetKey = self.getAppleWidgetKey(self.response.text)
        except Exception as e:
            raise Exception("requestAppletWidgetKey: Apple Widget Key query failed", 
                             self.urlKey,
                             repr(e))
        print(self.appleWidgetKey)
        
    def login (self):
        self.accountName = self.parseAccountName(input("User: "))
        password = getpass.getpass()
        self.session.verify = True
        self.session.headers.update(self.getAuthenticationRequestHeader())
        self.response = self.session.post(self.urlSignIn ,#+ self.appleWidgetKey,
                                          self.getAuthenticationRequestPayload(password))
        self.checkStatusCode()
        
    def parseAccountName (self, accountName):
        cleanAccountName = self.stripSpaces(self.cleanSpecialChar(accountName))
        if '@' not in cleanAccountName:
            cleanAccountName += self.mailBase
        return cleanAccountName

    def getAppleWidgetKey (self, data):
        widgetKey = ''
        query = "widgetKey="
        foundAt = data.find(query)
        if foundAt == -1:
            raise Exception("getAppleWidgetKey: Apple Widget Key could not be found")
        foundAt += len(query)
        char = data[foundAt]
        while char.isalnum():
            widgetKey += char
            foundAt += 1
            char = data[foundAt]
        return widgetKey 

    def checkStatusCode (self):
        if self.response.status_code > 400:
            raise Exception("HTTP Bad Response", self.response.status_code)

    def cleanSpecialChar (self, text):
        cleanText = text
        for char in self._ESCAPE_CHAR:
            cleanText = cleanText.replace(char, '')
        return cleanText
    
    def stripSpaces (self, text):
        return text.replace(' ', '')
    
if __name__ == "__main__":
    myI = PyiCloudService()
    myI.requestAppleWidgetKey()
    myI.login()
