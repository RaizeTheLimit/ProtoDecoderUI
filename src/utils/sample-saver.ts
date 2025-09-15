import fs from "fs";
import path from "path";
import { DecodedProto } from "../types";

interface SampleConfig {
    enabled: boolean;
    save_directory: string;
    max_samples_per_method: number;
    endpoints: string[];
}

interface SavedSample {
    methodId: string;
    methodName: string;
    timestamp: string;
    request: any;
    response: any;
    rawRequest: string;
    rawResponse: string;
}

interface SampleFile {
    filename: string;
    filepath: string;
    timestamp: number;
    methodId: string;
}

class SampleSaver {
    private config: SampleConfig;
    private savedSamples: Map<string, SampleFile[]> = new Map();
    private saveDirectory: string;

    constructor(config: SampleConfig) {
        this.config = config;
        this.saveDirectory = path.resolve(config.save_directory);
        this.initializeStorage();
        this.loadExistingSamples();
    }

    private initializeStorage(): void {
        if (!this.config.enabled) return;

        if (!fs.existsSync(this.saveDirectory)) {
            fs.mkdirSync(this.saveDirectory, { recursive: true });
            console.log(`Created sample storage directory: ${this.saveDirectory}`);
        }
    }

    private loadExistingSamples(): void {
        if (!this.config.enabled) return;

        if (fs.existsSync(this.saveDirectory)) {
            const files = fs.readdirSync(this.saveDirectory);

            files.forEach(file => {
                const match = file.match(/^(\d+)_.*_(\d+)\.json$/);
                if (match) {
                    const methodId = match[1];
                    const timestamp = parseInt(match[2]);
                    const filepath = path.join(this.saveDirectory, file);

                    const samples = this.savedSamples.get(methodId) || [];
                    samples.push({
                        filename: file,
                        filepath: filepath,
                        timestamp: timestamp,
                        methodId: methodId
                    });
                    this.savedSamples.set(methodId, samples);
                }
            });

            // Sort samples by timestamp for each method
            for (const [, samples] of this.savedSamples.entries()) {
                samples.sort((a, b) => a.timestamp - b.timestamp);
            }
        }
    }

    private getTimestamp(): string {
        return new Date().toISOString();
    }

    private deleteOldestSample(methodId: string): void {
        const samples = this.savedSamples.get(methodId);
        if (samples && samples.length > 0) {
            const oldest = samples.shift();
            if (oldest) {
                try {
                    fs.unlinkSync(oldest.filepath);
                    console.log(`Deleted oldest sample: ${oldest.filename}`);
                } catch (error) {
                    console.error(`Failed to delete old sample: ${error}`);
                }
            }
        }
    }

    private shouldSave(endpoint: string): boolean {
        if (!this.config.enabled) return false;
        if (!this.config.endpoints.includes(endpoint)) return false;
        return true;
    }

    public async saveSample(
        request: DecodedProto,
        response: DecodedProto | null,
        rawRequest: string,
        rawResponse: string,
        endpoint: string
    ): Promise<void> {
        if (!request || !request.methodId) return;
        if (!this.shouldSave(endpoint)) return;

        const methodSamples = this.savedSamples.get(request.methodId) || [];

        // If we've reached the max samples for this method, delete the oldest
        if (methodSamples.length >= this.config.max_samples_per_method) {
            this.deleteOldestSample(request.methodId);
        }

        const sample: SavedSample = {
            methodId: request.methodId,
            methodName: request.methodName,
            timestamp: this.getTimestamp(),
            request: request.data,
            response: response ? response.data : null,
            rawRequest: rawRequest,
            rawResponse: rawResponse
        };

        const safeMethodName = request.methodName.replace(/[^a-zA-Z0-9_-]/g, '_');
        const timestamp = Date.now();
        const filename = `${request.methodId}_${safeMethodName}_${timestamp}.json`;
        const filepath = path.join(this.saveDirectory, filename);

        try {
            fs.writeFileSync(filepath, JSON.stringify(sample, null, 2));

            // Update our tracking
            const samples = this.savedSamples.get(request.methodId) || [];
            samples.push({
                filename: filename,
                filepath: filepath,
                timestamp: timestamp,
                methodId: request.methodId
            });
            this.savedSamples.set(request.methodId, samples);

            console.log(`Saved sample for method ${request.methodId} (${request.methodName}): ${filename}`);
        } catch (error) {
            console.error(`Failed to save sample: ${error}`);
        }
    }

    public async savePair(
        request: DecodedProto,
        response: DecodedProto,
        rawRequest: string,
        rawResponse: string,
        endpoint: string
    ): Promise<void> {
        await this.saveSample(request, response, rawRequest, rawResponse, endpoint);
    }
}

export default SampleSaver;