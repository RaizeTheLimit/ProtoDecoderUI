export const b64Decode = (data: string) => {
  return Buffer.from(data, "base64");
};

export * from "./web-stream-buffer"
