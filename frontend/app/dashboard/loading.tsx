import { PageSkeleton } from "@/components/PageSkeleton";

export default function Loading() {
  return <PageSkeleton blocks={2} message="Opening your certificates…" />;
}
