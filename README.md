<!-- define variables -->
[1.1]: http://i.imgur.com/M4fJ65n.png (ATTENTION)
# ProtoDecoderUI [![Test Build](https://github.com/RaizeTheLimit/ProtoDecoderUI/actions/workflows/test.yml/badge.svg)](https://github.com/RaizeTheLimit/ProtoDecoderUI/actions/workflows/test.yml)

![alt text][1.1] <strong><em>`The contents of this repo are a proof of concept and are for educational use only`</em></strong>![alt text][1.1]<br/>

ProtoDecodeUI is a Tool to help analyze incoming and outgoing game data for Pokemon GO.

### Note that this repo is designed to be used with yarn and not npm. Doubts see: [yarn-setup](https://github.com/RaizeTheLimit/ProtoDecoderUI?tab=readme-ov-file#yarn-setup) 

### Support
Supports Decoding Requests and Response Messages

```
Default Port: 8081 (seen config file)
Request Route: /debug
Response Route: /raw
Web Interface to View Protos: /
Traffic Route mode /traffic
Golbat Route mode /golbat


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

### Support for Golbat interfaces
**Sent to** `/golbat`

```js
interface CombinedMessage {
    username: string 
    trainerlvl?: number
    contents : [
        {
            type: number
            request: string
            payload: string
            have_ar?: boolean
        }
    ]
}
```

### Requirements

```
Node 16 + (Tested on as low as version 16.14.0)
Yarn or NPM package manager
```

## Setup and Running

```bash
git clone git@github.com:RaizeTheLimit/ProtoDecoderUI.git
cd ./ProtoDecoderUI
```

### Important

**Copy and adjust config file**
```bash
# Copy the config.json file
cp src/config/example.config.json src/config/config.json
```

### Yarn setup:
```bash
npm install yarn -g
yarn
yarn build
yarn start
```

## Credits

 - [--=FurtiF™=-](https://github.com/sponsors/Furtif) for putting in the hard work of supplying Protos with every release ❤️
   If you would like to support him and future Proto Updates, please [sponsor](https://github.com/sponsors/Furtif) him on GitHub!
  
