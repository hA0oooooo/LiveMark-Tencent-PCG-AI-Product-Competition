import { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-lg border border-line bg-white p-5 shadow-sm ${className}`}>{children}</section>;
}

export function CardTitle({ children }: { children: ReactNode }) {
  return <h2 className="mb-3 text-base font-semibold text-ink">{children}</h2>;
}
