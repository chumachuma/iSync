import requests
import getpass

class PyiCloud:
    def __init__ (self):
        self.urlBase = "https://www.icloud.com/"
        self.mailBase = "@icloud.com"
        self.urlSignIn = "https://idmsa.apple.com/appleauth/auth/signin"

        self.accountName = ''

    def getRequestPayload (self, username, password):
        return {"accountName": username,
                "password": password,
                "rememberMe": False, 
                "trustTokens": []
                }

class PyiCloudService (PyiCloud):
    def __init__ (self):
        super(PyiCloudService, self).__init__()
        self._ESCAPE_CHAR = ",;&%!?|(){}[]~>*\'\"\\"

    def login (self):
        self.accountName = self.parseAccountName(input("User: "))
        password = getpass.getpass()
        myRequest = requests.get(self.urlSignIn, self.getRequestPayload(self.accountName, password))
        
    def parseAccountName (self, accountName):
        cleanAccountName = self.stripSpaces(self.cleanSpecialChar(accountName))
        if '@' not in cleanAccountName:
            cleanAccountName += self.mailBase
        return cleanAccountName

    def cleanSpecialChar (self, text):
        cleanText = text
        for char in self._ESCAPE_CHAR:
            cleanText = cleanText.replace(char, '')
        return cleanText
    
    def stripSpaces (self, text):
        return text.replace(' ', '')
    
if __name__ == "__main__":
    myI = PyiCloudService()
    myI.login()
