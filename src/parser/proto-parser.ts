import { b64Decode } from "../utils";
import { requestMessagesResponses } from "../constants";
import { DecodedProto } from "../types";

// For decode dynamics action social.
let action_social = 0;
/**
 * Callback as used by {@link DecoderInternalPayloadAsResponse}.
 * @type {function}
 * @param {number|any}
 */
/**
 * Returns decoded proto as JSON. Uses Tuples by https://github.com/Furtif/pogo-protos/blob/master/test/test.js, if that implemented.
 */
function DecoderInternalPayloadAsResponse(method: number, data: any): any {
    // Reset value.
    action_social = 0;
    let proto_tuple: any = Object.values(requestMessagesResponses)[method];
    let result: any = { Not_Implemented_yet: data };
    for (let i = 0; i < Object.keys(requestMessagesResponses).length; i++) {
        proto_tuple = Object.values(requestMessagesResponses)[i];
        const my_req = proto_tuple[0];
        if (my_req == method) {
            if (proto_tuple[2] != null && b64Decode(data)) {
                try {
                    result = proto_tuple[2].decode(b64Decode(data)).toJSON();
                    /*
                    // This not need more because protos as replaced bytes for the proto.
                    if (method == 10010) {
                        let profile = POGOProtos.Rpc.PlayerPublicProfileProto.decode(b64Decode(result.friend[0].player.public_data)).toJSON();
                        result.friend[0].player.public_data = profile;
                    }
                    */
                }
                catch (error) {
                    console.error(`Intenal ProxySocial decoder ${my_req} Error: ${error}`);
                    let err = {
                        Error: error,
                        Data: data
                    };
                    result = err;
                }
            }
            return result;
        }
    }
    return result;
}

function remasterOrCleanMethodString(str: string) {
    return str.replace(/^REQUEST_TYPE_/, '')
        .replace(/^METHOD_/, '')
        .replace(/^PLATFORM_/, '')
        .replace(/^SOCIAL_ACTION_/, '')
        .replace(/^GAME_ANTICHEAT_ACTION_/, '')
        .replace(/^GAME_BACKGROUND_MODE_ACTION_/, '')
        .replace(/^GAME_IAP_ACTION_/, '')
        .replace(/^GAME_LOCATION_AWARENESS_ACTION_/, '')
        .replace(/^GAME_ACCOUNT_REGISTRY_ACTION_/, '')
        .replace(/^GAME_FITNESS_ACTION_/, '')
        .replace(/^TITAN_PLAYER_SUBMISSION_ACTION_/, '');
}

export const decodePayloadTraffic = (methodId: number, content: any, dataType: string): DecodedProto[] => {
    let parsedProtoData: DecodedProto[] = [];
    const decodedProto = decodeProto(methodId, content, dataType);
    if (typeof decodedProto !== "string") {
        parsedProtoData.push(decodedProto);
    }
    return parsedProtoData;
};

export const decodePayload = (contents: any, dataType: string): DecodedProto[] => {
    let parsedProtoData: DecodedProto[] = [];
    for (const proto of contents) {
        const methodId = proto.method;
        const data = proto.data;
        const decodedProto = decodeProto(methodId, data, dataType);
        if (typeof decodedProto !== "string") {
            parsedProtoData.push(decodedProto);
        }
    }
    return parsedProtoData;
};

export const decodeProto = (method: number, data: string, dataType: string): DecodedProto | string => {
    let returnObject: DecodedProto | string = "Not Found";
    for (let i = 0; i < Object.keys(requestMessagesResponses).length; i++) {
        let foundMethod: any = Object.values(requestMessagesResponses)[i];
        let foundMethodString: string = Object.keys(requestMessagesResponses)[i];
        const foundReq = foundMethod[0];
        if (foundReq == method) {
            if (foundMethod[1] != null && dataType === "request") {
                try {
                    let parsedData = foundMethod[1].decode(b64Decode(data)).toJSON();
                    if (foundMethod[0] === 5012 || foundMethod[0] === 600005) {
                        action_social = parsedData.action;
                        Object.values(requestMessagesResponses).forEach(val => {
                            let req: any = val;
                            if (req[0] == action_social && req[1] != null && parsedData.payload && b64Decode(parsedData.payload)) {
                                parsedData.payload = req[1].decode(b64Decode(parsedData.payload)).toJSON();
                            }
                        });
                    }
                    returnObject = {
                        methodId: foundMethod[0],
                        methodName: remasterOrCleanMethodString(foundMethodString),
                        data: parsedData,
                    };
                } catch (error) {
                    console.error(`Error parsing request ${foundMethodString} -> ${error}`);
                }
            } else if (dataType === "request") {
                console.warn(`Request ${foundMethod[0]} Not Implemented`)
            }
            if (foundMethod[2] != null && dataType === "response") {
                try {
                    let parsedData = foundMethod[2].decode(b64Decode(data)).toJSON();
                    if (foundMethod[0] === 5012 && action_social > 0 && parsedData.payload) {
                        parsedData.payload = DecoderInternalPayloadAsResponse(action_social, parsedData.payload);
                    }
                    else if (foundMethod[0] === 600005 && action_social > 0 && parsedData.payload) {
                        parsedData.payload = DecoderInternalPayloadAsResponse(action_social, parsedData.payload);
                    }
                    returnObject = {
                        methodId: foundMethod[0],
                        methodName: remasterOrCleanMethodString(foundMethodString),
                        data: parsedData,
                    };
                } catch (error) {
                    console.error(`Error parsing response ${foundMethodString} method: [${foundReq}] -> ${error}`);
                }
            } else if (dataType === "response") {
                console.warn(`Response ${foundReq} Not Implemented`)
            }
        }
    }
    return returnObject;
};