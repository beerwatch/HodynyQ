# HodynyQ
RP2040 to replace RPi Linux in my desktop alarm clock and enable functionality extension towards wearable watch


# Note about Google Oauth2 application identity key
The Oauth2/client_secret.json file contains Google Oauth2 application identity. It is used to present application information and security policies and for tracking application use. To actually access Google API a personified access token is needed. 
The access token is generated during process that incorporates actual person's log-in. The resulting personified client token file shall be uploaded to the directory and named client_token.json.

For more information see https://developers.google.com/identity/protocols/oauth2. Because of limitations listed in https://developers.google.com/identity/protocols/oauth2/limited-input-device#allowedscopes I had to use https://developers.google.com/identity/protocols/oauth2/native-app. I don't really understand why there is such limitation when your application wants only to read calendar items while these can be shared to anybody by the user.

The application components around SGAPI.py showcase minimal Micropython code to interact with Google Oauth2 that leaves some of RP2040 RAM free to run other tasks. Yes, I did it again.
