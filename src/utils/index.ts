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

export function redirect_post(url_rediret: string, redirect_data: any) {
    const url = parse(url_rediret);
    const request = http.request({
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        host: url.hostname,
        port: url.port,
        path: url.path
    });
    request.write(JSON.stringify(redirect_data));
    request.end();
}

export * from "./web-stream-buffer";
