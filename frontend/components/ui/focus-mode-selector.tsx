"use client";

import { cn } from "@/lib/utils";
import { FOCUS_MODES } from "@/lib/constants";

interface FocusModeSelectorProps {
  value: string;
  onChange: (mode: string) => void;
  className?: string;
  compact?: boolean;
}

export function FocusModeSelector({
  value,
  onChange,
  className,
  compact = false,
}: FocusModeSelectorProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-1 p-1 rounded-lg bg-muted/50 border border-border",
        className
      )}
      role="tablist"
    >
      {FOCUS_MODES.map((mode) => (
        <button
          key={mode.id}
          role="tab"
          type="button"
          onClick={() => onChange(mode.id)}
          className={cn(
            "flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-sm font-medium transition-colors",
            value === mode.id
              ? "bg-primary text-primary-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground hover:bg-accent"
          )}
          title={mode.label}
        >
          <span className="text-base leading-none">{mode.icon}</span>
          {!compact && <span>{mode.label}</span>}
        </button>
      ))}
    </div>
  );
}
