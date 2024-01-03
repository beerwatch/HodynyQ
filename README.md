# HodynyQ
RP2040 to replace RPi Linux in my desktop alarm clock and enable functionality extension towards wearable watch


# Note about Google Oauth2 application identity key
The Oauth2/client_secret.json file contains Google Oauth2 application identity. It is used to present application information and security policies and for tracking application use. To actually access Google API a personified access token is needed. 
The access token is generated during process that incorporates actual person's log-in. The resulting personified client token file shall be uploaded to the directory and named client_token.json.

The application components around SGAPI.py showcase minimal Micropython code to interact with Google Oauth2 that leaves some of RP2040 RAM free to run other tasks.

See https://developers.google.com/identity/protocols/oauth2
