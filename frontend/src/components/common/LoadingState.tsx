interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = 'h-4 w-full' }: SkeletonProps) {
  return <div className={`animate-pulse-soft rounded-md bg-white/5 ${className}`} />;
}

export function CardSkeleton({ height = 240 }: { height?: number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-surface p-5">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="mt-3 h-3 w-48" />
      <div className="mt-4 animate-pulse-soft rounded-xl bg-white/5" style={{ height }} />
    </div>
  );
}

export function StatTileSkeleton() {
  return (
    <div className="rounded-2xl border border-white/10 bg-surface p-4">
      <Skeleton className="h-3 w-20" />
      <Skeleton className="mt-4 h-7 w-24" />
      <Skeleton className="mt-2 h-3 w-16" />
    </div>
  );
}
