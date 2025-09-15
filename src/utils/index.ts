import { networkInterfaces } from "os";
import http from "http";
import { parse } from "url";
import { WebStreamBuffer } from "./web-stream-buffer";
import { decodePayloadTraffic } from "../parser/proto-parser";

export const b64Decode = (data: string) => {
    if (!data || data === "") {
        return Buffer.alloc(0);
    }
    return Buffer.from(data, "base64");
};

export function moduleConfigIsAvailable() {
    try {
        require.resolve("../config/config.json");
        return true;
    } catch (e) {
        return false;
    }
}

export function getIPAddress() {
    var interfaces = networkInterfaces();
    for (var devName in interfaces) {
        var iface: any = interfaces[devName];
        for (var i = 0; i < iface.length; i++) {
            var alias = iface[i];
            if (alias.family === 'IPv4' && alias.address !== '127.0.0.1' && !alias.internal)
                return alias.address;
        }
    }
    return '0.0.0.0';
}

export function handleData(incoming: WebStreamBuffer, outgoing: WebStreamBuffer, identifier: any, parsedData: string, sampleSaver?: any) {
    for (let i = 0; i < parsedData['protos'].length; i++) {
        const rawRequest = parsedData['protos'][i].request || "";
        const rawResponse = parsedData['protos'][i].response || "";

        const parsedRequestData = decodePayloadTraffic(
            parsedData['protos'][i].method,
            rawRequest,
            "request"
        );
        const parsedResponseData = decodePayloadTraffic(
            parsedData['protos'][i].method,
            rawResponse,
            "response"
        );

        // Save sample if enabled
        if (sampleSaver && parsedRequestData.length > 0 && parsedResponseData.length > 0) {
            sampleSaver.savePair(parsedRequestData[0], parsedResponseData[0], rawRequest, rawResponse, "traffic");
        }

        if (typeof parsedRequestData === "string") {
            incoming.write({ error: parsedRequestData });
        } else {
            for (let parsedObject of parsedRequestData) {
                parsedObject.identifier = identifier;
                incoming.write(parsedObject);
            }
        }

        if (typeof parsedResponseData === "string") {
            outgoing.write({ error: parsedResponseData });
        } else {
            for (let parsedObject of parsedResponseData) {
                parsedObject.identifier = identifier;
                outgoing.write(parsedObject);
            }
        }
    }
}

export function redirect_post_golbat(redirect_url: string, redirect_token: string, redirect_data: any) {
    const url = parse(redirect_url);
    const headers = {
        "Content-Type": "application/json"
    };
    if (redirect_token) {
        headers["Authorization"] = "Bearer " + redirect_token;
    }
    const request = http.request({
        method: "POST",
        headers: headers,
        host: url.hostname,
        port: url.port,
        path: url.path
    });
    request.write(redirect_data);
    request.end();
}

export * from "./web-stream-buffer";
