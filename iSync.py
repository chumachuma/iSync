import requests
from json import dumps as json
from uuid import uuid1 as generateClientID
import getpass

__author__ = "JiaJiunn Chiou"
__license__= ""
__version__= "0.0.1"
__status__ = "Prototype"

class Pointer:
    def __init__ (self, value):
        try:
            self.value = value.value
        except:
            self.value = value

    def __call__ (self, value=None):
        if value == None:
            return self.value
        try:
            self.value = value.value
        except:
            self.value = value


class HTTPService:
    def __init__ (self, session, response=None, origin=None, referer=None):
        self.userAgent = "Python (X11; Linux x86_64)" 
        try:
            self.session = session.session
            self.response = session.response
            self.origin = session.origin 
            self.referer = session.referer 
        except:
            session = session
            self.response = response
            self.origin = origin
            self.referer = referer


class IdmsaAppleService(HTTPService):
    def __init__ (self, session):
        super(IdmsaAppleService, self).__init__(session)
        self.url = "https://idmsa.apple.com"
        self.urlAuth = self.url + "/appleauth/auth/signin?widgetKey="

        self.appleSessionToken = None

    def requestAppleSessionToken (self, user, password, appleWidgetKey):
        self.session.headers = self.getRequestHeader(appleWidgetKey)
        self.response.value = self.session.post(self.urlAuth + appleWidgetKey,
                self.getRequestPayload(user, password))
        try:
            self.appleSessionToken = self.response().headers["X-Apple-Session-Token"]
        except Exception as e:
            raise Exception("requestAppleSessionToken: Apple Session Token query failed", 
                             self.urlAuth, repr(e))
        return self.appleSessionToken

    def getRequestHeader (self, appleWidgetKey):
        if not appleWidgetKey:
            raise NameError("getSetupQueryParameters: clientID not found")
        return {
                "Accept": "application/json, text/javascript",
                "Content-Type": "application/json",
                "User-Agent": self.userAgent,
                "X-Apple-Widget-Key": appleWidgetKey,
                "X-Requested-With": "XMLHttpRequest",
                "Origin": self.origin,
                "Referer": self.referer,
                }

    def getRequestPayload (self, user, password):
        if not user:
            raise NameError("getAuthenticationRequestPayload: user not found")
        if not password:
            raise NameError("getAuthenticationRequestPayload: password not found")
        return json({
            "accountName": user,
            "password": password,
            "rememberMe": False,
            }) 


class SetupiCloudService(HTTPService):
    def __init__ (self, session):
        super(SetupiCloudService, self).__init__(session)
        self.url = "https://setup.icloud.com/setup/ws/1"
        self.urlKey = self.url + "/validate"
        self.urlLogin = self.url + "/accountLogin"
        
        self.appleWidgetKey = None
        self.cookies = None
        self.dsid = None
    
    def requestAppleWidgetKey (self, clientID):
        #self.urlBase + "/system/cloudos/16CHotfix21/en-us/javascript-packed.js"
        self.session.headers = self.getRequestHeader()
        self.response.value = self.session.get(self.urlKey, params=self.getSetupQueryParameters(clientID))
        try:
            self.appleWidgetKey = self.findQyery(self.response().text, "widgetKey=")
        except Exception as e:
            raise Exception("requestAppletWidgetKey: Apple Widget Key query failed", 
                             self.urlKey, repr(e))
        return self.appleWidgetKey
     
    def requestCookies (self, appleSessionToken, clientID):
        self.session.headers = self.getRequestHeader()
        self.response.value = self.session.post(self.urlLogin,
                                          self.getLoginRequestPayload(appleSessionToken),
                                          params=self.getSetupQueryParameters(clientID))
        try:
            self.cookies = self.response().headers["Set-Cookie"]
        except Exception as e:
            raise Exception("requestCookies: Cookies query failed", 
                             self.urlLogin, repr(e))
        try:
            self.dsid = self.response().json()["dsInfo"]["dsid"]
        except Exception as e:
            raise Exception("requestCookies: dsid query failed", 
                             self.urlLogin, repr(e))
        return self.cookies, self.dsid

    def findQyery (self, data, query):
        response = ''
        foundAt = data.find(query)
        if foundAt == -1:
            raise Exception("findQyery: " + query + " could not be found in data")
        foundAt += len(query)
        char = data[foundAt]
        while char.isalnum():
            response += char
            foundAt += 1
            char = data[foundAt]
        return response 


    def getRequestHeader (self):
        return {
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Content-Type": "text/plain",
                "User-Agent": self.userAgent,
                "Origin": self.origin,
                "Referer": self.referer,
               }

    def getSetupQueryParameters (self, clientID):
        if not clientID:
            raise NameError("getSetupQueryParameters: clientID not found")
        return {
                "clientBuildNumber": "16CHotfix21",
                "clientID": clientID,
                "clientMasteringNumber": "16CHotfix21",
               }

    def getLoginRequestPayload (self, appleSessionToken):
        if not appleSessionToken:
            raise NameError("getLoginRequestPayload: X-Apple-ID-Session-Id not found")
        return json({
                "dsWebAuthToken": appleSessionToken,
                "extended_login": False,
                })

    
class ICloudService(HTTPService):
    def __init__ (self):
        super(ICloudService, self).__init__(session)
        self.url = "https://www.icloud.com"
        self.urlApp = self.url + "/applications"

class ReminderWidget (HTTPService):
    def __init__ (self, session):
        super(ReminderWidget, self).__init__()
        self.session = session
        self.urlReminder = self.urlApp + "/reminders/current/en-gb/index.html"

    def getRequestHeader (self, cookie):
        return {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Cookie": cookie,
                "Host": self.urlBase,
                "Referer": self.urlBase,
                "Upgrade-Insecure-Requests":"1",
                "User-Agent": self.userAgent,
               }

    def getReminderList (self, cookie):
        self.session.headers.update(self.getRequestHeader(cookie))
        response = self.session.get(self.urlReminder)
        response.raise_for_status()
        print(response.text)


class PyiCloudService (HTTPService):
    def __init__ (self):
        self.session = requests.Session()
        self.session.verify = True
        self.response = Pointer(None)
        self.origin = "https://www.icloud.com"
        self.referer = "https://www.icloud.com"
        super(PyiCloudService, self).__init__(self)

        self._ESCAPE_CHAR = ",;&%!?|(){}[]~>*\'\"\\"

        self.clientID = self.generateClientID()

        self.idmsaApple = IdmsaAppleService(self)
        self.setupiCloud = SetupiCloudService(self)

    def login (self):
        user = self.parseAccountName(input("User: "))
        password = getpass.getpass()
        self.initSession(user, password)

    def initSession (self,user, password):
        clientID = self.clientID = self.generateClientID()
        print(clientID)
        widgetKey = self.setupiCloud.requestAppleWidgetKey(clientID)
        print(widgetKey)
        sessionToken = self.idmsaApple.requestAppleSessionToken(user, password, widgetKey)
        print(sessionToken)
        cookies, dsid = self.setupiCloud.requestCookies(sessionToken, clientID)
        return (cookies, dsid)

    def generateClientID (self):
        return str(generateClientID()).upper()

    def parseAccountName (self, accountName):
        cleanAccountName = self.stripSpaces(self.cleanSpecialChar(accountName))
        if '@' not in cleanAccountName:
            cleanAccountName += "@icloud.com"
        return cleanAccountName


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
