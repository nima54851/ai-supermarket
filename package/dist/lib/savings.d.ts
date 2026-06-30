import type { ResponsesUsage } from "./responses.js";
export interface ModelSavings {
    requests: number;
    savingsUsd: number;
    tokens: number;
}
export interface SavingsState {
    version: number;
    totalSavingsUsd: number;
    totalTokens: number;
    totalRequests: number;
    firstRecordedAt: string | null;
    lastRecordedAt: string | null;
    byModel: Record<string, ModelSavings>;
    notice: {
        lastShownAtRequest: number;
        lastMilestoneUsd: number;
    };
}
export declare function savingsPath(): string;
export declare function resolveBaselineModel(): string;
export declare function estimateTokens(text: string | undefined): number;
export declare function computeCallSavings(inputTokens: number, outputTokens: number, baseline: string, zgpuModel: string): {
    tokens: number;
    savingsUsd: number;
};
export declare function readSavings(): SavingsState;
export declare function writeSavings(state: SavingsState): void;
export declare function resetSavings(): void;
export declare function shouldShowNotice(state: SavingsState, random?: () => number): boolean;
export interface RecordInput {
    model: string;
    usage?: ResponsesUsage;
    inputText?: string;
    outputText?: string;
}
export declare function recordAndMaybeNotify(input: RecordInput): void;
export declare function formatNotice(state: SavingsState): string;
export declare function formatReport(state: SavingsState): string;
//# sourceMappingURL=savings.d.ts.map