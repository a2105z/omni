/**
 * Shared constants.
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const FOCUS_MODES = ["general", "academic", "code", "writing"] as const;
export type FocusMode = (typeof FOCUS_MODES)[number];
