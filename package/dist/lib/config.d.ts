export interface Config {
    apiKey?: string;
    projectId?: string;
}
export declare function configDir(): string;
export declare function configPath(): string;
export declare function readConfig(): Config;
export declare function writeConfig(cfg: Config): void;
//# sourceMappingURL=config.d.ts.map