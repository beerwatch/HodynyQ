import SHttp, json, time, gc

class SGApi( object ):
    def __init__( self, calID = 'default' ):
        self._listener = None
        self.backuri = 'http://localhost'
        self.secretFile = '/Oauth2/client_secret.json'
        self.tokenFile = '/Oauth2/client_token.json'
        self.calID = calID

        self._secret = None
        self._token = None

    def RFC2time( self, T ):
        return time.mktime([int(T[0:4]),int(T[5:7]),int(T[8:10]),int(T[11:13]),int(T[14:16]),int(T[17:19]),0,0])-int(T[19]+'1')*(int(T[20:22])*3600+int(T[23:25])*60)

    def _loadJson( self, fileName ):
        try:
            fi = open( fileName )
        except:
            return None
        js = json.load(fi)
        fi.close()
        return js

    def _dumpJson( self, fileName , js ):
        fo = open( fileName , 'w' )
        json.dump(js, fo)
        fo.close()

    def _loadSecret( self ):
        if not self._secret:
            self._secret = self._loadJson( self.secretFile )

    def _loadToken( self ):
        if not self._token:
            self._token = self._loadJson( self.tokenFile )

    def _listen( self ):
        if not self._listener:
            import socket
            self._listener = socket.socket()
            self._listener.bind( socket.getaddrinfo( '0.0.0.0' , 80)[0][-1] )
            self._listener.listen(1)

    def _unlisten( self ):
        if self._listener:
            self._listener.close()
            self._listener = None

    def SGA_WfGetForm( self ):
        # dodat formular zarizeni pro navstevu do Googlu ("workflow" autorizace zarizeni, krok 1)
        self._loadSecret()
        s1 = '''<!DOCTYPE html><head><title>Presmerovani do Google OAuth2</title></head>\r
        <body bgcolor="#ffffff" text="#000000" link="#0000cc" vlink="#551a8b" alink="#ff0000">\r
        <form method="POST" action="{2}">\r
        <input type="hidden" name="client_id" value="{1}">\r
        <input type="hidden" name="redirect_uri" value="{0}">\r
        <input type="hidden" name="scope" value="https://www.googleapis.com/auth/calendar.events.readonly">\r
        <input type="hidden" name="response_type" value="code">\r
        <input type="submit" value="Autorizovat zarizeni v Google">\r
        </form>\r
        </body>'''.format(    self.backuri    , self._secret['installed']['client_id']    , self._secret['installed']['auth_uri']    )
        self._listen()
        server = SHttp.SHttp()
        server._accept( self._listener )
        server.receiveHttpRequest()
        server.headers={'content-type' : 'text/html' , 'content-length' : len(s1), 'connection' : 'close' }
        server.status=200
        server.sendHttpResponse()
        server.write(s1)
        server.close()
        self._unlisten()

    def SGA_WfGetCodeFromBackUri( self ):
        # obslouzit backuri a ziskat kod pro ziskani tokenu
        self._listen()
        server = SHttp.SHttp()
        server._accept( self._listener )
        server.receiveHttpRequest()
        code = server.getqryval( 'code' )
        s1 = '''<!DOCTYPE html><head><title>Ziskani autentikacniho kodu zarizeni z Google OAuth2</title></head>\r
        <body bgcolor="#ffffff" text="#000000" link="#0000cc" vlink="#551a8b" alink="#ff0000">\r
        <h1>OK</h1><p>{0}</p>\r
        </body>'''.format(    code    )
        server.headers = {'content-type' : 'text/html' , 'content-length' : len(s1), 'connection' : 'close' }
        server.status = 200
        server.sendHttpResponse()
        server.write(s1)
        server.close()
        self._unlisten()

        self.SGA_WfGetTokenFromCode( code )

    def SGA_WfGetTokenFromCode( self , code ):
        #vymenit kod za token
        self._loadSecret()
        s1='''code={3}&client_id={1}&client_secret={2}&grant_type=authorization_code&redirect_uri={0}'''.format(
            self.backuri
            ,self._secret['installed']['client_id']
            ,self._secret['installed']['client_secret']
            ,code
            )
        client = SHttp.SHttp()
        client.method='POST'
        client._splitUri( self._secret['installed']['token_uri'] )		# 'https://oauth2.googleapis.com/token'
        client.headers={'Content-Type' : 'application/x-www-form-urlencoded', 'content-length' : len(s1), 'Connection' : 'close' }
        client.sendHttpRequest()
        client.write(s1)
        client.receiveHttpResponse()
        if client.status == 200:
            jw = json.load( client._conn )
            self._dumpJson( self.tokenFile , jw )
        client.close()

    def SGA_RefreshToken( self ):
        # obnovit token
        self._loadToken()
        self._loadSecret()
        s1='''refresh_token={0}&client_id={1}&client_secret={2}&grant_type=refresh_token'''.format(
            self._token['refresh_token']
            ,self._secret['installed']['client_id']
            ,self._secret['installed']['client_secret']
            )
        client = SHttp.SHttp()
        client.method='POST'
        client._splitUri( self._secret['installed']['token_uri'] ) # 'https://oauth2.googleapis.com/token'
        client.headers={'Content-Type' : 'application/x-www-form-urlencoded', 'content-length' : len(s1), 'Connection' : 'close' , 'Accept' : 'application/json' }
        gc.collect()
        client.sendHttpRequest()
        client.write(s1)
        client.receiveHttpResponse()
        try:
            if client.status == 200:
                jw = json.load( client._conn )
                self._token['token_type'] =   jw['token_type']
                self._token['access_token'] = jw['access_token']
                self._token['expires_in'] = jw['expires_in']
                tx = time.time() + jw['expires_in']
                self._token['expires_on']=tx
                self._dumpJson( self.tokenFile , self._token )
        finally:
            pass
        client.close()

    def SGA_CalGetNextItems( self , count = 6 ):
        # nacist polozky kalendare
        self._loadToken()
        if 'expires_on' not in self._token or time.time() > self._token['expires_on']:
            self.SGA_RefreshToken()
        jw = None
        gc.collect()
        client = SHttp.SHttp()
        try:
            client._splitUri('https://www.googleapis.com/calendar/v3/calendars/{}/events'.format( client.urlencode( self.calID ) ) )
            tNow=time.gmtime()
            tNowRFC = '{:04d}-{:02d}-{:02d}T{:02d}%3A{:02d}%3A{:02d}Z'.format( tNow[0],tNow[1],tNow[2],tNow[3],tNow[4],tNow[5] )
            client.qry = 'maxResults={}&orderBy=startTime&singleEvents=true&fields=defaultReminders%2Citems(organizer%2Cstart%2Creminders%2CeventType%2Csummary)&timeMin={}'.format(count, tNowRFC)
            client.headers = { 'Authorization' : self._token['token_type'] + ' ' +self._token['access_token'] , 'Accept' : 'application/json', 'Connection' : 'close' }
            gc.collect()
            client.sendHttpRequest()
            client.receiveHttpResponse()
        finally:
            if client.status == 200:
                jw = json.load( client._conn )
            client.close()
        return jw

    def GAPI_getUpdateNextAlarm( self ):
        # get next 6 calendar items from the net
        try:
            jw = self.SGA_CalGetNextItems(6)
            if jw == None:
                return None
        except OSError:
            return None
        # find next alarm
        Curr = None
        tCurr = 4262661632
        tNow = time.time()
        for item in jw['items']:
            if 'dateTime' in item['start']:
                ta = self.RFC2time( item['start']['dateTime'] )
            else:
                continue

            if ta >= tNow and ta < tCurr:
                tCurr = ta
                Curr = [ ta, ta, item ]
                if item['reminders']['useDefault']:
                    enr = jw['defaultReminders']
                else:
                    if 'overrides' in item['reminders']:
                        enr = item['reminders']['overrides']
                    else:
                        continue
                tActiveRemind = tCurr
                for rmd in enr:
                    dr = rmd['minutes'] * 60
                    tr = ta - dr
                    if tr < tActiveRemind:
                        tActiveRemind = tr
                        Curr = [ tr, ta, item ]
        return Curr
