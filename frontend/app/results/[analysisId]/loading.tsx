import { PageSkeleton } from "@/components/PageSkeleton";

export default function Loading() {
  return (
    <PageSkeleton
      width="max-w-3xl"
      blocks={3}
      message="Loading your results. The first one after a quiet spell can take up to a minute."
    />
  );
}
