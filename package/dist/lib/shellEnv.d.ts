export interface UpsertResult {
    path: string;
    shell: "zsh" | "bash" | "fish" | "posix" | "windows";
    note?: string;
}
export declare function upsertEnvExport(name: string, value: string): UpsertResult;
//# sourceMappingURL=shellEnv.d.ts.map