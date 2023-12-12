export class WebStreamBuffer {
    readers: { read(data: object) }[] = [];

    write(data: object) {
        for (let reader of this.readers) {
            reader.read(data);
        }
    }

    addReader(reader: { read(data: object) }) {
        this.readers.push(reader);
    }

    removeReader(reader: { read(data: object) }) {
        var index = this.readers.indexOf(reader);
        if (index !== -1) {
            this.readers.splice(index, 1);
            return true;
        }
        return false;
    }
}