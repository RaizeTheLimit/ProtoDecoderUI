"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const http_1 = __importDefault(require("http"));
const fs_1 = __importDefault(require("fs"));
const utils_1 = require("./utils");
const proto_parser_1 = require("./parser/proto-parser");
let config = require("./config/example.config.json");
if ((0, utils_1.moduleConfigIsAvailable)()) {
    config = require("./config/config.json");
}
const incomingProtoWebBufferInst = new utils_1.WebStreamBuffer();
const outgoingProtoWebBufferInst = new utils_1.WebStreamBuffer();
const portBind = config["default_port"];
const httpServer = http_1.default.createServer(function (req, res) {
    let incomingData = [];
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
                if (config["redirect_to_golbat_url"]) {
                    (0, utils_1.redirect_post_golbat)(config["redirect_to_golbat_url"], JSON.stringify(parsedData));
                }
                const identifier = parsedData['username'];
                for (let i = 0; i < parsedData['contents'].length; i++) {
                    const parsedRequestData = (0, proto_parser_1.decodePayloadTraffic)(parsedData['contents'][i].type, parsedData['contents'][i].request, "request");
                    if (typeof parsedRequestData === "string") {
                        incomingProtoWebBufferInst.write({ error: parsedRequestData });
                    }
                    else {
                        for (let parsedObject of parsedRequestData) {
                            parsedObject.identifier = identifier;
                            incomingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                    const parsedResponseData = (0, proto_parser_1.decodePayloadTraffic)(parsedData['contents'][i].type, parsedData['contents'][i].payload, "response");
                    if (typeof parsedResponseData === "string") {
                        outgoingProtoWebBufferInst.write({ error: parsedResponseData });
                    }
                    else {
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
                    const parsedRequestData = (0, proto_parser_1.decodePayloadTraffic)(parsedData['protos'][i].method, parsedData['protos'][i].request, "request");
                    if (typeof parsedRequestData === "string") {
                        incomingProtoWebBufferInst.write({ error: parsedRequestData });
                    }
                    else {
                        for (let parsedObject of parsedRequestData) {
                            parsedObject.identifier = identifier;
                            incomingProtoWebBufferInst.write(parsedObject);
                        }
                    }
                    const parsedResponseData = (0, proto_parser_1.decodePayloadTraffic)(parsedData['protos'][i].method, parsedData['protos'][i].response, "response");
                    if (typeof parsedResponseData === "string") {
                        outgoingProtoWebBufferInst.write({ error: parsedResponseData });
                    }
                    else {
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
                const parsedResponseData = (0, proto_parser_1.decodePayload)(parsedData.contents, "response");
                if (typeof parsedResponseData === "string") {
                    incomingProtoWebBufferInst.write({ error: parsedResponseData });
                }
                else {
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
                const parsedRequestData = (0, proto_parser_1.decodePayload)(parsedData.contents, "request");
                if (typeof parsedRequestData === "string") {
                    outgoingProtoWebBufferInst.write({ error: parsedRequestData });
                }
                else {
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
        case "/icons/play.png":
            res.writeHead(200, { "Content-Type": "image/png" });
            const pagePlay = fs.readFileSync("./dist/views/icons/play.png");
            res.end(pagePlay);
            break;
        case "/icons/pause.png":
            res.writeHead(200, { "Content-Type": "image/png" });
            const pagePause = fs.readFileSync("./dist/views/icons/pause.png");
            res.end(pagePause);
            break;
        case "/icons/stop.png":
            res.writeHead(200, { "Content-Type": "image/png" });
            const pageStop = fs.readFileSync("./dist/views/icons/stop.png");
            res.end(pageStop);
            break;
        case "/css/style.css":
            res.writeHead(200, { "Content-Type": "text/css" });
            const pageCssL = fs_1.default.readFileSync("./dist/views/css/style.css");
            res.end(pageCssL);
            break;
        case "/json-viewer/jquery.json-viewer.css":
            res.writeHead(200, { "Content-Type": "text/css" });
            const pageCss = fs_1.default.readFileSync("node_modules/jquery.json-viewer/json-viewer/jquery.json-viewer.css");
            res.end(pageCss);
            break;
        case "/json-viewer/jquery.json-viewer.js":
            res.writeHead(200, { "Content-Type": "text/javascript" });
            const pageJs = fs_1.default.readFileSync("node_modules/jquery.json-viewer/json-viewer/jquery.json-viewer.js");
            res.end(pageJs);
            break;
        case "/":
            res.writeHead(200, { "Content-Type": "text/html" });
            const pageHTML = fs_1.default.readFileSync("./dist/views/print-protos.html");
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
        read: function (data) {
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
        read: function (data) {
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
    console.log(`Server start access of this in urls: http://localhost:${portBind} or WLAN mode http://${(0, utils_1.getIPAddress)()}:${portBind}`);
});
//# sourceMappingURL=index.js.map