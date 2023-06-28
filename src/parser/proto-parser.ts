import { b64Decode } from "../utils";
import { requestMessagesResponses } from "../constants";
import { DecodedProto } from "../types";


export const decodePayload = (
  contents: any,
  dataType: string
): DecodedProto[] => {
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

export const decodeProto = (
  method: number,
  data: string,
  dataType: string
): DecodedProto | string => {
  let returnObject: DecodedProto | string = "Not Found";
  for (let i = 0; i < Object.keys(requestMessagesResponses).length; i++) {
    let foundMethod: any = Object.values(requestMessagesResponses)[i];
    let foundMethodString: string = Object.keys(requestMessagesResponses)[i];

    const foundReq = foundMethod[0];
    if (foundReq == method) {
      if (foundMethod[1] != null && dataType === "request") {
        try {
          let parsedData = foundMethod[1].decode(b64Decode(data)).toJSON();
          returnObject = {
            methodId: foundMethod[0],
            methodName: foundMethodString,
            data: parsedData,
          };
        } catch (error) {
          console.log(`Error parsing request ${foundMethodString} `);
        }
      } else if (dataType === "request") {
        console.log(`Request ${foundMethod[0]} Not Implemented`)
      }

      if (foundMethod[2] != null && dataType === "response") {
        try {
          let parsedData = foundMethod[2].decode(b64Decode(data)).toJSON();
          returnObject = {
            methodId: foundMethod[0],
            methodName: foundMethodString,
            data: parsedData,
          };
        } catch (error) {
          console.log(`Error parsing response ${foundMethodString} `);
        }
      } else if (dataType === "response") {
        console.log(`Response ${foundMethod[0]} Not Implemented`)
      }
    }
  }
  return returnObject;
};
