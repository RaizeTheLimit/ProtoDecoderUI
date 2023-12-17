import http from "http";
import fs from "fs";
import { WebStreamBuffer, getIPAddress, moduleConfigIsAvailable, redirect_post_golbat } from "./utils";
import { decodePayload, decodePayloadTraffic } from "./parser/proto-parser";

// try looking if config file exists...
let config = require("./config/example.config.json");
if (moduleConfigIsAvailable()) {
    config = require("./config/config.json");
}

// utils
const incomingProtoWebBufferInst = new WebStreamBuffer();
const outgoingProtoWebBufferInst = new WebStreamBuffer();
const portBind = config["default_port"];

// server
const httpServer = http.createServer(function (req, res) {
    let incomingData: Array<Buffer> = [];
    switch (req.url) {
        case "/golbat":
            req.on("data", function (chunk) {
                incomingData.push(chunk);
            });
            req.on("end", function () {
                const requestData = incomingData.join("");
                let parsedData = JSON.parse(requestData);
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end("");
                // redirect because endpoint is in use there, leave null to ignore.
                // ex http://123.123.123.123:9001/raw
                // this need a test ping ok or throw for better.
                if (config["redirect_to_golbat_url"]) {
                    redirect_post_golbat(config["redirect_to_golbat_url"], JSON.stringify(parsedData));
                }
                const identifier = parsedData['username'];
                for (let i = 0; i < parsedData['contents'].length; i++) {
                    const parsedRequestData = decodePayloadTraffic(
                        parsedData['contents'][i].type,
                        parsedData['contents'][i].request,
                        "request"
                    );
                    if (typeof parsedRequestData === "string") {
                        incomingProtoWebBufferInst.write({ error: parsedRequestData });
                    } else {
                        for (let parsedObject of parsedRequestData) {
                            parsedObject.identifier = identifier;
                            incomingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                    const parsedResponseData = decodePayloadTraffic(
                        parsedData['contents'][i].type,
                        parsedData['contents'][i].payload,
                        "response"
                    );
                    if (typeof parsedResponseData === "string") {
                        outgoingProtoWebBufferInst.write({ error: parsedResponseData });
                    } else {
                        for (let parsedObject of parsedResponseData) {
                            parsedObject.identifier = identifier;
                            outgoingProtoWebBufferInst.write(parsedObject);
                        }
                    }
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
                for (let i = 0; i < parsedData['protos'].length; i++) {
                    const parsedRequestData = decodePayloadTraffic(
                        parsedData['protos'][i].method,
                        parsedData['protos'][i].request,
                        "request"
                    );
                    if (typeof parsedRequestData === "string") {
                        incomingProtoWebBufferInst.write({ error: parsedRequestData });
                    } else {
                        for (let parsedObject of parsedRequestData) {
                            parsedObject.identifier = identifier;
                            incomingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                    const parsedResponseData = decodePayloadTraffic(
                        parsedData['protos'][i].method,
                        parsedData['protos'][i].response,
                        "response"
                    );
                    if (typeof parsedResponseData === "string") {
                        outgoingProtoWebBufferInst.write({ error: parsedResponseData });
                    } else {
                        for (let parsedObject of parsedResponseData) {
                            parsedObject.identifier = identifier;
                            outgoingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                }
            });
            break;
        case "/raw":
            req.on("data", (chunk) => {
                incomingData.push(chunk);
            });
            req.on("end", () => {
                const requestData = incomingData.join("");
                let parsedData = JSON.parse(requestData);
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end("");
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
            });
            break;
        case "/debug":
            req.on("data", function (chunk) {
                incomingData.push(chunk);
            });
            req.on("end", function () {
                const requestData = incomingData.join("");
                let parsedData = JSON.parse(requestData);
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end("");
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
            });
            break;
        case "/images/favicon.png":
            res.writeHead(200, { "Content-Type": "image/png" });
            const favicon = fs.readFileSync("./dist/views/images/favicon.png");
            res.end(favicon);
            break;
        case "/css/style.css":
            res.writeHead(200, { "Content-Type": "text/css" });
            const pageCssL = fs.readFileSync("./dist/views/css/style.css");
            res.end(pageCssL);
            break;
        case "/json-viewer/jquery.json-viewer.css":
            res.writeHead(200, { "Content-Type": "text/css" });
            const pageCss = fs.readFileSync("node_modules/jquery.json-viewer/json-viewer/jquery.json-viewer.css");
            res.end(pageCss);
            break;
        case "/json-viewer/jquery.json-viewer.js":
            res.writeHead(200, { "Content-Type": "text/javascript" });
            const pageJs = fs.readFileSync("node_modules/jquery.json-viewer/json-viewer/jquery.json-viewer.js");
            res.end(pageJs);
            break;
        case "/":
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
var incoming = io.of("/incoming").on("connection", function (socket) {
    const reader = {
        read: function (data: object) {
            incoming.emit("protos", data);
        },
    };
    incomingProtoWebBufferInst.addReader(reader);
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
    socket.on("disconnect", function () {
        outgoingProtoWebBufferInst.removeReader(reader);
    });
});

httpServer.keepAliveTimeout = 0;
httpServer.listen(portBind, function () {
    console.log(`Server start access of this in urls: http://localhost:${portBind} or WLAN mode http://${getIPAddress()}:${portBind}`);
});
