import type { InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from "react";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent ${props.className || ""}`} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent ${props.className || ""}`} />;
}

export function Label({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="grid gap-1 text-sm text-muted">
      <span>{label}</span>
      {children}
    </label>
  );
}
