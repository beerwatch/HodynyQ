import socket, ssl, gc
from array import array

class SHttp( object ):
    _uri_reserved = '!#$&\'()*+,/:;=?@[]'
    def __init__(self):
        self.method = 'GET'
        self.level='HTTP/1.0'
        self.chunksize = 5120 #3040		# adjust to leaky TLS implementation... :-(

        self.prot = None
        self.host = None
        self.port = 80
        self.path = None
        self.qry = None
        self.tag = None
        self.status = 0

        self.headers = {}

        self.doTLS = False
        self.keyfile = None
        self.certfile = None
        self.cert_reqs = ssl.CERT_NONE
        self.cadata = None
        
        self._conn = None

    def _splitUri(self, uri:str):
        s = uri.split('#')
        self.tag = s[1] if len(s) > 1 else ''
        s = s[0].split('?')
        self.qry = s[1] if len(s) > 1 else ''
        s = s[0].split('/',3)
        self.host = s[2] if len(s) > 2 else s[0]
        self.path = '/' + ( s[3] if len(s) > 3 else s[1] if len(s) == 2 else '' )
        self.prot = s[0] if len(s[0]) > 2 else 'http:'
        self.doTLS = True if self.prot == 'https:' else False
        s=self.host.split(':')
        if len( s ) == 2:
            self.port = s[1]
            self.host = s[0]
        else:
            self.port = 443 if self.doTLS else 80
        if len( self.host ) == 0:
            self.port = self.prot=''

    def urlencode( self, s: str):
        n=0
        for c in s:
            if self._uri_reserved.find(c) >= 0 or ord(c) > 126 or ord(c) < 32:
                n = n + 2
        if n == 0:
            return s
        o = array( 'B' , [ 0 ] * ( len(s) + n ) )
        n = 0
        for c in s:
            if self._uri_reserved.find(c) >= 0 or ord(c) > 126 or ord(c) < 32:
                o[n    ] = ord('%')
                v = hex(ord(c)).replace('x','0')
                o[n + 1] = ord(v[-2])
                o[n + 2] = ord(v[-1])
                n = n + 3
            else:
                o[n    ] = ord(c) if c != ' ' else ord('+')
                n = n + 1
        return str(o, 'utf-8')

    def urldecode( self, s: str):
        n=0
        for c in s:
            if c == '%':
                n = n + 2
        if n == 0:
            return s
        o = array( 'B' , [ 0 ] * ( len(s) - n ) )
        m = n = 0
        while m < len(s):
            c = s[ m ]
            if c == '%':
                o[ n ] = int( s[ m + 1 ] + s[ m + 2 ] , 16 )
                m = m + 3
            else:
                o[n    ] = ord(c) if c != '+' else ord(' ')
                m = m + 1
            n = n + 1
        return str(o, 'utf-8')

    def _connect(self):
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self._conn = socket.socket()
        self._conn.connect(addr)
        if self.doTLS:
            self._conn = ssl.wrap_socket( self._conn, server_hostname=self.host, server_side=False )

    def _accept(self,listener):
        self._conn,self.client = listener.accept()
        if self.doTLS:
            self._conn = ssl.wrap_socket( self._conn, server_side=True , keyfile=self.keyfile, certfile=self.keyfile, cert_reqs=self.cert_reqs, cadata=self.cadata )

    def _sendHeaders(self):
        if isinstance(self.headers, dict):
            ae=''
            for k in self.headers:
                ae+=k+':'+str(self.headers[k])+'\r\n'
        else:
            ae = '\r\n'.join( n + ':' + v for n,v in self.headers )+'\r\n'
#        print(ae)
        self._conn.write(bytes("%s\r\n" % (ae), 'utf8'))

    def _receiveHeaders(self):
        self.headers = {}
        ae = self._conn.readline()
        while len(ae) > 2:
#            print(ae )
            ae = str(ae,'utf-8').split(':', 2 )
            self.headers[ae[0].strip().lower()] = ae[1].strip()
            ae = self._conn.readline()

    def header(self,key):
        ley=key.lower()
        if isinstance(self.headers, dict):
            return self.headers.get(key.lower(), '')
        for n,v in self.headers:
            if key == n.lower():
                return v
        return ''

    def sendHttpRequest(self):
        if not self._conn:
            self._connect()
        ae = bytes('%s %s %s\r\nHost: %s\r\n' % (self.method, self.path + '?' + self.qry if self.qry else self.path, self.level, self.host), 'utf-8')
#        print(ae)
        self._conn.write( ae )
        self._sendHeaders()

    def receiveHttpResponse(self):
        ae = self._conn.readline()
        ae = str(ae.strip(),'utf-8').split(' ', 3 )
        self.level = ae[0]
        self.status = int(ae[1])
        self.statusText = ae[2].strip()
        self._receiveHeaders()

    def receiveHttpRequest(self):
        ae = self._conn.readline()
        ae = str(ae.strip(),'utf-8').split(' ', 3 )
        self.method = ae[0]
        self.path = ae[1]
        self.level = ae[2].strip()
        self._receiveHeaders()

    def sendHttpResponse(self):
        self._conn.write(bytes('%s %d\r\n' % (self.level, self.status), 'utf8'))
        self._sendHeaders()

    def write(self,buf):
        return self._conn.write(buf)

    def read(self):
        return self._conn.read()

    def read(self, num):
        return self._conn.read(num)

    def close(self):
        #self._conn.setsockopt(socket.SO_LINGER, [ 1, 60])
        #self._conn.close()

        #self._conn.shutdown()
        #while self._conn.read(1024):
        #    pass
        #self._conn.close()

        import time
        time.sleep_ms(600)
        self._conn.close()

        self._conn = None

    def processBody( self, cback ):
        rlen=self.header('Content-Length')
        if len(rlen) > 0:
            rlen = int(rlen)
            while rlen > 0:
                ae=self._conn.read(rlen if rlen < self.chunksize else self.chunksize)
                l=len(ae)
                cback( ae )
                rlen -= l
                if l < 1:
                    break
        else:
            while True:
                ae=self._conn.read(self.chunksize)
                cback( ae )
                if not ae:
                    break

"""
    def _test_splitUri(self):
        for uri in [ 'http://abcd:1234/path' , '//abcd:1234', '//abcd/path', '/abcd', 'https://abcd:1234?q=1', 'http://abcd/path#tag', 'https://abcd/path/to/resource' ] :
            self._splitUri(uri)
            print( uri, self.prot, self.host, self.port, self.path, self.qry, self.tag , self.doTLS, sep='\t')

    def _test_urlencdec(self):
        s = 'Ahoj'
        print(s)
        t=self.urlencode(s)
        print( t )
        print( self.urldecode(t))
        s = 'Ahoj ! #$&\'()*+,/:;=?@[]'
        print(s)
        t=self.urlencode(s)
        print( t )
        print( self.urldecode(t))
"""
#SHttp()._test_splitUri()
#SHttp()._test_urlencdec()

"""
# for repeated server testing create listener only once...
try:
    dir().index('sListen')
except:
    sListen = socket.socket()
    sListen.bind( socket.getaddrinfo( '0.0.0.0' , 80)[0][-1] )
    sListen.listen(1)

print('ready')
"""

"""
# test (TLS) server - TLS no workee, no server-side compiled for myp!!!!
server = SHttp()
server._conn,client = sListen.accept()
server.keyfile = '/cer/mbox.cica.cz.key'
server.certfile = '/cer/fullchain.cer'
print( client )
sc = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sc.load_cert_chain(server.certfile, server.keyfile)
server=sc.wrap_socket( server._conn )
"""
"""
server.doTLS=True
server.keyfile = '/cer/mbox.cica.cz.key'
server.certfile = '/cer/fullchain.cer'
server.cert_reqs = ssl.CERT_NONE
server.cadata = '/cer/ca.cer'

server._accept(sListen)
print( server.client )
sc = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server=sc.wrap_socket( sListen.accept() )
#server = ssl.wrap_socket( sListen.accept(), keyfile=server.keyfile, certfile=server.certfile, cert_reqs = server.cert_reqs )
server.receiveHttpRequest()
rlen=int(server.header('Content-Length') or 0)
while rlen > 0:
    ae=server.read(rlen)
    print(rlen,ae)
    rlen -= len(ae)
server.headers={'content-type' : 'text/plain' , 'content-length' : '7', 'connection' : 'close' }
#server.headers=[ ('content-type' , 'text/plain' ),( 'content-length' , '7' ), ( 'connection' , 'close' ) ]
server.status=200
server.sendHttpResponse()
server.write('Konec\r\n')
server.close()
server=None
"""

"""
# test (TLS) client - workee, no checks against MITM compiled for myp!
def printLen( ae ):
    print(len(ae))

client = SHttp()
client._splitUri('https://forum.phsos.cz/')
print(client.host)
#client.headers={'Content-Type' : 'text/plain' , 'Content-Length' : '0', 'Connection' : 'close' }
client.headers={'Content-Type' : 'text/plain', 'Connection' : 'close' }
client.sendHttpRequest()
client.receiveHttpResponse()
print(client.status)
client.processBody( printLen )
client.close()
client=None
"""
