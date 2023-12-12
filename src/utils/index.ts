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

export * from "./web-stream-buffer";
