import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
export function configDir() {
    return join(homedir(), ".zerogpu");
}
export function configPath() {
    return join(configDir(), "config.json");
}
export function readConfig() {
    const path = configPath();
    if (!existsSync(path))
        return {};
    try {
        const raw = readFileSync(path, "utf8");
        const parsed = JSON.parse(raw);
        return parsed && typeof parsed === "object" ? parsed : {};
    }
    catch {
        return {};
    }
}
export function writeConfig(cfg) {
    mkdirSync(configDir(), { recursive: true, mode: 0o700 });
    writeFileSync(configPath(), JSON.stringify(cfg, null, 2), { mode: 0o600 });
}
//# sourceMappingURL=config.js.map