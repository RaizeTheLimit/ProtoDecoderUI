# ProtoDecoderUI

ProtoDecodeUI is a Tool to help analyze incoming and outgoing game data. 


### Support
Supports Decoding Requests and Response Messages

```
Default Port: 8081
Request Route: /debug
Response Route: /raw
Web Interface to View Protos: /
Traffic Route mode /traffic


Web Interface: 

Supports Start/Pause/Clearing of the proto stream
Method Filtering by Whitelisting or Blackisting (whitelist overrides Blacklist)

```


### Incoming Data Types
Both endpoints support the same basic interface supplied by most popular MITM, **You must have at least one of the optional parameters as an identifier**

```js

interface IncomingData {
      uuid?: string
      deviceName?: string
      devicename?: string
      instanceName?: string
      contents : [
          {
            method: number,
            data: string
          }
      ]
}

```

### Support for Trafficlight interfaces
**Sent to** `/traffic`

```js
interface CombinedMessage {
    rpcid?: number
    rpcstatus?: number
    rpchandle?: number
    protos: [
        {
            method: number
            request: string
            response: string
        }
    ]
}
```

### Requirements

```
Node 16 + (Tested on as low as version 16.14.0
Yarn or NPM package manager
```


## Setup and Running

```
git clone git@github.com:RaizeTheLimit/ProtoDecoderUI.git
cd ./ProtoDecoderUI
```


if you would like to change the port, create a `.env` file in the project root with the following
```
PORT=8081  # Desired Port
```

Yarn setup:
```
yarn
yarn build
yarn start
```

NPM setup:
```
npm install && npm run build
npm run start
```



## Credits

 - FurtiF for putting in the hard work of supplying Protos with every release ❤️
   If you would like to support him and future Proto Updates, please sponsor him on GitHub!
  
