import { networkInterfaces } from "os";
import http from "http";
import { parse } from "url";

export const b64Decode = (data: string) => {
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
