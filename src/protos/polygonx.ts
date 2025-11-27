import protobuf from "protobufjs";

// Define the PolygonX proto schema programmatically using protobufjs
const root = protobuf.Root.fromJSON({
    nested: {
        RawProtoCollection: {
            fields: {
                protos: { rule: "repeated", type: "RawProto", id: 1 },
                pushGatewayProtos: { rule: "repeated", type: "RawPushGatewayProto", id: 2 }
            }
        },
        RawProto: {
            fields: {
                method: { type: "int32", id: 1 },
                proto: { type: "bytes", id: 2 },
                request: { type: "bytes", id: 3 },
                trainerId: { type: "string", id: 4 },
                trainerLevel: { type: "int32", id: 5 },
                hasGeotargetedArScanQuest: { type: "bool", id: 6 }
            }
        },
        RawPushGatewayProto: {
            fields: {
                method: { type: "int32", id: 1 },
                proto: { type: "bytes", id: 2 },
                trainerId: { type: "string", id: 4 },
                trainerLevel: { type: "int32", id: 5 },
                hasGeotargetedArScanQuest: { type: "bool", id: 6 }
            }
        }
    }
});

export const RawProtoCollection = root.lookupType("RawProtoCollection");

// Type definitions for decoded messages
export interface RawProto {
    method: number;
    proto: Uint8Array;
    request: Uint8Array;
    trainerId: string;
    trainerLevel: number;
    hasGeotargetedArScanQuest: boolean;
}

export interface RawPushGatewayProto {
    method: number;
    proto: Uint8Array;
    trainerId: string;
    trainerLevel: number;
    hasGeotargetedArScanQuest: boolean;
}

export interface RawProtoCollectionMessage {
    protos: RawProto[];
    pushGatewayProtos: RawPushGatewayProto[];
}
