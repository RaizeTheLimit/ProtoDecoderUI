import http from "http";
import fs from "fs";
import crypto from "crypto";
import { WebStreamBuffer, getIPAddress, handleData, moduleConfigIsAvailable, redirect_post_golbat } from "./utils";
import { decodePayload, decodePayloadTraffic, remasterOrCleanMethodString } from "./parser/proto-parser";
import SampleSaver from "./utils/sample-saver";
import { requestMessagesResponses } from "./constants";

// try looking if config file exists...
let config = require("./config/example.config.json");
if (moduleConfigIsAvailable()) {
    config = require("./config/config.json");
}

// utils
const incomingProtoWebBufferInst = new WebStreamBuffer();
const outgoingProtoWebBufferInst = new WebStreamBuffer();
const portBind = config["default_port"];

// Initialize sample saver
const sampleSaver = config.sample_saving ? new SampleSaver(config.sample_saving) : null;

// Authentication setup
const WEB_PASSWORD = config["web_password"];
const AUTH_REQUIRED = WEB_PASSWORD !== null && WEB_PASSWORD !== undefined && WEB_PASSWORD !== "";
const sessions = new Set<string>();

// Helper functions for authentication
function generateSessionToken(): string {
    return crypto.randomBytes(32).toString("hex");
}

function parseCookies(cookieHeader: string | undefined): Record<string, string> {
    const cookies: Record<string, string> = {};
    if (!cookieHeader) return cookies;

    cookieHeader.split(';').forEach(cookie => {
        const parts = cookie.trim().split('=');
        if (parts.length === 2) {
            cookies[parts[0]] = parts[1];
        }
    });
    return cookies;
}

function isAuthenticated(req: http.IncomingMessage): boolean {
    if (!AUTH_REQUIRED) return true;

    const cookies = parseCookies(req.headers.cookie);
    const sessionToken = cookies['session_token'];
    return !!(sessionToken && sessions.has(sessionToken));
}

function requireAuth(req: http.IncomingMessage, res: http.ServerResponse): boolean {
    if (!isAuthenticated(req)) {
        res.writeHead(302, { Location: '/login' });
        res.end();
        return false;
    }
    return true;
}

// server
const httpServer = http.createServer(function (req, res) {
    let incomingData: Array<Buffer> = [];

    // Authentication routes
    if (req.url === "/login" && req.method === "GET") {
        if (isAuthenticated(req)) {
            res.writeHead(302, { Location: '/' });
            res.end();
            return;
        }
        res.writeHead(200, { "Content-Type": "text/html" });
        const loginHTML = fs.readFileSync("./dist/views/login.html");
        res.end(loginHTML);
        return;
    }

    if (req.url === "/auth/login" && req.method === "POST") {
        req.on("data", function (chunk) {
            incomingData.push(chunk);
        });
        req.on("end", function () {
            try {
                const requestData = incomingData.join("");
                const parsedData = JSON.parse(requestData);

                if (parsedData.password === WEB_PASSWORD) {
                    const sessionToken = generateSessionToken();
                    sessions.add(sessionToken);

                    res.writeHead(200, {
                        "Content-Type": "application/json",
                        "Set-Cookie": `session_token=${sessionToken}; HttpOnly; Path=/; Max-Age=86400`
                    });
                    res.end(JSON.stringify({ success: true }));
                } else {
                    res.writeHead(401, { "Content-Type": "application/json" });
                    res.end(JSON.stringify({ success: false, message: "Invalid password" }));
                }
            } catch (error) {
                res.writeHead(400, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ success: false, message: "Invalid request" }));
            }
        });
        return;
    }

    if (req.url === "/auth/logout" && req.method === "POST") {
        const cookies = parseCookies(req.headers.cookie);
        const sessionToken = cookies['session_token'];
        if (sessionToken) {
            sessions.delete(sessionToken);
        }

        res.writeHead(200, {
            "Content-Type": "application/json",
            "Set-Cookie": "session_token=; HttpOnly; Path=/; Max-Age=0"
        });
        res.end(JSON.stringify({ success: true }));
        return;
    }

    if (req.url === "/auth/status" && req.method === "GET") {
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ authRequired: AUTH_REQUIRED }));
        return;
    }

    if (req.url === "/api/methods" && req.method === "GET") {
        if (!requireAuth(req, res)) return;

        // Build complete method list from constants
        const methodsList = Object.entries(requestMessagesResponses).map(([rawName, tuple]) => ({
            id: String(tuple[0]),                          // Method ID as string
            rawName: rawName,                              // Original constant name
            cleanName: remasterOrCleanMethodString(rawName), // Cleaned display name
            hasRequest: tuple[1] !== null,                 // Has request proto
            hasResponse: tuple[2] !== null                 // Has response proto
        }));

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(methodsList));
        return;
    }

    switch (req.url) {
        case "/golbat":
            req.on("data", function (chunk) {
                incomingData.push(chunk);
            });
            req.on("end", function () {
                try {
                    const requestData = incomingData.join("");
                    let parsedData = JSON.parse(requestData);
                    res.writeHead(200, { "Content-Type": "application/json" });
                    res.end("");
                    if (Array.isArray(parsedData)) {
                        console.error("Incoming Data is an array, need to be single object");
                        return;
                    }
                    // Validate required fields
                    if (!parsedData['contents'] || !Array.isArray(parsedData['contents'])) {
                        console.error("Invalid golbat data: 'contents' field missing or not an array");
                        return;
                    }
                    if (parsedData['contents'].length === 0) {
                        console.error("Invalid golbat data: 'contents' array is empty");
                        return;
                    }
                    // redirect because endpoint is in use there, leave null to ignore.
                    // ex http://123.123.123.123:9001/raw
                    // this need a test ping ok or throw for better.
                    if (config["redirect_to_golbat_url"]) {
                        try {
                            redirect_post_golbat(config["redirect_to_golbat_url"], config["redirect_to_golbat_token"], JSON.stringify(parsedData));
                        }
                        catch (err) {
                            console.error("Endpoint golbat offline or bad!" + err);
                        }
                    }
                    const identifier = parsedData['username'];
                    for (let i = 0; i < parsedData['contents'].length; i++) {
                    const rawRequest = parsedData['contents'][i].request || "";
                    const rawResponse = parsedData['contents'][i].payload || "";

                    const parsedRequestData = decodePayloadTraffic(
                        parsedData['contents'][i].type,
                        rawRequest,
                        "request"
                    );
                    const parsedResponseData = decodePayloadTraffic(
                        parsedData['contents'][i].type,
                        rawResponse,
                        "response"
                    );

                    // Save sample if enabled
                    if (sampleSaver && parsedRequestData.length > 0 && parsedResponseData.length > 0) {
                        sampleSaver.savePair(parsedRequestData[0], parsedResponseData[0], rawRequest, rawResponse, "golbat");
                    }

                    if (typeof parsedRequestData === "string") {
                        incomingProtoWebBufferInst.write({ error: parsedRequestData });
                    } else {
                        for (let parsedObject of parsedRequestData) {
                            parsedObject.identifier = identifier;
                            incomingProtoWebBufferInst.write(parsedObject);
                        }
                    }

                    if (typeof parsedResponseData === "string") {
                        outgoingProtoWebBufferInst.write({ error: parsedResponseData });
                    } else {
                        for (let parsedObject of parsedResponseData) {
                            parsedObject.identifier = identifier;
                            outgoingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                }
                } catch (error) {
                    console.error("Error processing golbat request:", error);
                }
            });
            break;
        case "/traffic":
            req.on("data", function (chunk) {
                incomingData.push(chunk);
            });
            req.on("end", function () {
                const identifier = config["trafficlight_identifier"];
                const requestData = incomingData.join("");
                let parsedData = JSON.parse(requestData);
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end("");
                if (Array.isArray(parsedData)) {
                    for (let i = 0; i < parsedData.length; i++) {
                        handleData(incomingProtoWebBufferInst, outgoingProtoWebBufferInst, identifier, parsedData[i], sampleSaver)
                    }
                } else {
                    handleData(incomingProtoWebBufferInst, outgoingProtoWebBufferInst, identifier, parsedData, sampleSaver)
                }
            });
            break;
        case "/raw":
            req.on("data", (chunk) => {
                incomingData.push(chunk);
            });
            req.on("end", () => {
                try {
                    const requestData = incomingData.join("");
                    let parsedData = JSON.parse(requestData);
                    res.writeHead(200, { "Content-Type": "application/json" });
                    res.end("");
                    // Validate required fields
                    if (!parsedData.contents) {
                        console.error("Invalid raw data: 'contents' field missing");
                        return;
                    }
                    const parsedResponseData = decodePayload(
                        parsedData.contents,
                        "response"
                    );
                    if (typeof parsedResponseData === "string") {
                        incomingProtoWebBufferInst.write({ error: parsedResponseData });
                    } else {
                        for (let parsedObject of parsedResponseData) {
                            parsedObject.identifier =
                                parsedData["uuid"] ||
                                parsedData["devicename"] ||
                                parsedData["deviceName"] ||
                                parsedData["instanceName"];
                            incomingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                } catch (error) {
                    console.error("Error processing raw request:", error);
                }
            });
            break;
        case "/debug":
            req.on("data", function (chunk) {
                incomingData.push(chunk);
            });
            req.on("end", function () {
                try {
                    const requestData = incomingData.join("");
                    let parsedData = JSON.parse(requestData);
                    res.writeHead(200, { "Content-Type": "application/json" });
                    res.end("");
                    // Validate required fields
                    if (!parsedData.contents) {
                        console.error("Invalid debug data: 'contents' field missing");
                        return;
                    }
                    const parsedRequestData = decodePayload(parsedData.contents, "request");
                    if (typeof parsedRequestData === "string") {
                        outgoingProtoWebBufferInst.write({ error: parsedRequestData });
                    } else {
                        for (let parsedObject of parsedRequestData) {
                            parsedObject.identifier =
                                parsedData["uuid"] ||
                                parsedData["devicename"] ||
                                parsedData["deviceName"] ||
                                parsedData["instanceName"];
                            outgoingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                } catch (error) {
                    console.error("Error processing debug request:", error);
                }
            });
            break;
        case "/images/favicon.png":
            if (!requireAuth(req, res)) break;
            res.writeHead(200, { "Content-Type": "image/png" });
            const favicon = fs.readFileSync("./dist/views/images/favicon.png");
            res.end(favicon);
            break;
        case "/css/style.css":
            if (!requireAuth(req, res)) break;
            res.writeHead(200, { "Content-Type": "text/css" });
            const pageCssL = fs.readFileSync("./dist/views/css/style.css");
            res.end(pageCssL);
            break;
        case "/json-viewer/jquery.json-viewer.css":
            if (!requireAuth(req, res)) break;
            res.writeHead(200, { "Content-Type": "text/css" });
            const pageCss = fs.readFileSync("node_modules/jquery.json-viewer/json-viewer/jquery.json-viewer.css");
            res.end(pageCss);
            break;
        case "/json-viewer/jquery.json-viewer.js":
            if (!requireAuth(req, res)) break;
            res.writeHead(200, { "Content-Type": "text/javascript" });
            const pageJs = fs.readFileSync("node_modules/jquery.json-viewer/json-viewer/jquery.json-viewer.js");
            res.end(pageJs);
            break;
        case "/":
            if (!requireAuth(req, res)) break;
            res.writeHead(200, { "Content-Type": "text/html" });
            const pageHTML = fs.readFileSync("./dist/views/print-protos.html");
            res.end(pageHTML);
            break;
        default:
            res.end("Unsupported url: " + req.url);
            break;
    }
});

var io = require("socket.io")(httpServer);

// Socket.IO authentication middleware
if (AUTH_REQUIRED) {
    io.use((socket, next) => {
        const cookieHeader = socket.handshake.headers.cookie;
        const cookies = parseCookies(cookieHeader);
        const sessionToken = cookies['session_token'];

        if (sessionToken && sessions.has(sessionToken)) {
            next();
        } else {
            next(new Error('Authentication required'));
        }
    });
}

var incoming = io.of("/incoming").on("connection", function (socket) {
    const reader = {
        read: function (data: object) {
            incoming.emit("protos", data);
        },
    };
    incomingProtoWebBufferInst.addReader(reader);
    socket.on("error", function (err) {
        console.log("WebSockets Error: ", err)
    })
    socket.on("disconnect", function () {
        incomingProtoWebBufferInst.removeReader(reader);
    });
});

var outgoing = io.of("/outgoing").on("connection", function (socket) {
    const reader = {
        read: function (data: object) {
            outgoing.emit("protos", data);
        },
    };
    outgoingProtoWebBufferInst.addReader(reader);
    socket.on("error", function (err) {
        console.log("WebSockets Error: ", err)
    })
    socket.on("disconnect", function () {
        outgoingProtoWebBufferInst.removeReader(reader);
    });
});

httpServer.keepAliveTimeout = 0;
httpServer.listen(portBind, function () {
    const authStatus = AUTH_REQUIRED ? "ENABLED - Password required to access web UI" : "DISABLED";
    const welcome = `
Server start access of this in urls: http://localhost:${portBind} or WLAN mode http://${getIPAddress()}:${portBind}.

    - Web Authentication: ${authStatus}

    - Clients MITM:
        1) --=FurtiF™=- Tools EndPoints: http://${getIPAddress()}:${portBind}/traffic or http://${getIPAddress()}:${portBind}/golbat (depending on the modes chosen)
        2) If Other set here...
        3) ...

ProtoDecoderUI is not responsible for your errors.
`;
    console.log(welcome);
});
