export declare const API_KEY_PREFIX = "zgpu-api-";
export type ValidationResult = {
    ok: true;
    key: string;
} | {
    ok: false;
    reason: string;
};
export declare function validateApiKey(input: string): ValidationResult;
export interface ResolvedKey {
    apiKey: string;
    source: "config file" | "env var";
}
export declare function getApiKey(): ResolvedKey | undefined;
export declare function validateProjectId(input: string): ValidationResult;
export interface ResolvedProjectId {
    projectId: string;
    source: "config file" | "env var";
}
export declare function getProjectId(): ResolvedProjectId | undefined;
//# sourceMappingURL=auth.d.ts.map