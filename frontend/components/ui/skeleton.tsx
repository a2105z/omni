import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

export function SearchInputSkeleton() {
  return (
    <div className="flex gap-2 border-2 border-border rounded-md p-2 bg-card">
      <Skeleton className="flex-1 h-12" />
      <Skeleton className="w-10 h-10 rounded" />
    </div>
  );
}

export function MessageSkeleton() {
  return (
    <div className="space-y-4 animate-in fade-in duration-300">
      <Skeleton className="h-10 w-3/4" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-4/5" />
      </div>
    </div>
  );
}

export function SourceCardSkeleton() {
  return (
    <div className="flex items-center gap-3 p-2 rounded border">
      <Skeleton className="w-8 h-8 rounded" />
      <div className="flex-1 space-y-1">
        <Skeleton className="h-3 w-32" />
        <Skeleton className="h-2 w-24" />
      </div>
    </div>
  );
}
