import requests
from json import dumps as json
from uuid import uuid1 as generateClientID
import getpass

__author__ = "JiaJiunn Chiou"
__license__= ""
__version__= "0.0.1"
__status__ = "Prototype"

class PyiCloud:
    def __init__ (self):
        self.urlBase = "https://www.icloud.com"
        self.urlAuth = "https://idmsa.apple.com"
        self.urlSignIn = self.urlAuth + "/appleauth/auth/signin?widgetKey="
        self.urlSetup = "https://setup.icloud.com/setup/ws/1"
        self.urlKey = self.urlSetup + "/validate"
        self.urlLogin = self.urlSetup + "/accountLogin"
        self.mailBase = "@icloud.com"

        self.session = requests.Session()
        self.response = None
        self.userAgent = "Python (X11; Linux x86_64)" 
        self.accountName = None
        self.appleWidgetKey = None
        self.clientID = self.generateClientID()
        self.appleSessionToken = None

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
    
    def getSetupQueryParameters (self):
        return {
                "clientBuildNumber": "16CHotfix21",
                "clientID": self.clientID,
                "clientMasteringNumber": "16CHotfix21"
               }

    def getLoginRequestPayload (self):
        if not self.appleSessionToken:
            raise NameError("getLoginRequestPayload: X-Apple-ID-Session-Id unavailable")
        return json({
                "dsWebAuthToken": self.appleSessionToken,
                "extended_login": False
                })

    def getSetupRequestHeader (self):
        return {
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Content-Type": "text/plain",
                "Origin": self.urlBase,
                "Referer": self.urlBase,
                "User-Agent": self.userAgent,
               }

    def generateClientID (self):
        return str(generateClientID()).upper()


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
        self.session.headers.update(self.getSetupRequestHeader())
        self.response = self.session.get(self.urlKey, params=self.getSetupQueryParameters())
        print(self.response.status_code)
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

        self.response = self.session.post(self.urlSignIn + self.appleWidgetKey,
                                          self.getAuthenticationRequestPayload(password))
        self.response.raise_for_status()
        print(self.response.headers)
        self.appleSessionToken = self.response.headers["X-Apple-Session-Token"]

        print(self.getLoginRequestPayload())
        self.session.headers.update(self.getSetupRequestHeader())
        self.response = self.session.post(self.urlLogin ,#+ self.getQueryString(self.getSetupQueryParameters()),
                                          self.getLoginRequestPayload(),
                                          params=self.getSetupQueryParameters())
        print("\n\nHEADERS")
        print(self.response.headers)
        print("\n\nTEXT")
        print(self.response.text)
        print(self.response.status_code)
        self.response.raise_for_status()
        
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

    def cleanSpecialChar (self, text):
        cleanText = text
        for char in self._ESCAPE_CHAR:
            cleanText = cleanText.replace(char, '')
        return cleanText
    
    def stripSpaces (self, text):
        return text.replace(' ', '').replace('\t', '')
    
if __name__ == "__main__":
    myI = PyiCloudService()
    myI.requestAppleWidgetKey()
    myI.login()
    
### TEST ###
    tPyiCloud = PyiCloud()
    #assert tPyiCloud.getQueryString({"a":"1", "b":"2", "c":False}) == "a=1&b=2&c=False"

    tPyiCloudService = PyiCloudService()
    tPyiCloudService.requestAppleWidgetKey()
    assert tPyiCloudService.appleWidgetKey == "83545bf919730e51dbfba24e7e8a78d2"
