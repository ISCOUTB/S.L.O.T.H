export function isEqual(a: unknown, b: unknown): boolean {
    if (a === b) return true;
    if (typeof a !== typeof b) return false;
    if (a && b && typeof a === "object") {
        if (Array.isArray(a) && Array.isArray(b)) {
            if (a.length !== b.length) return false;
            for (let i = 0; i < a.length; i++) {
                if (!isEqual(a[i], b[i])) return false;
            }
            return true;
        }
        const aKeys = Object.keys(a as object);
        const bKeys = Object.keys(b as object);
        if (aKeys.length !== bKeys.length) return false;
        for (const key of aKeys) {
            if (!isEqual((a as any)[key], (b as any)[key])) return false;
        }
        return true;
    }
    return false;
}
