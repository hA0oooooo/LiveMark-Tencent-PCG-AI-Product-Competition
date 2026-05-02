import { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className = "", variant = "primary", ...props }: Props) {
  const base = "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60";
  const styles = {
    primary: "bg-brand text-white hover:bg-[#bd3049]",
    secondary: "border border-line bg-white text-ink hover:bg-surface",
    ghost: "text-ink hover:bg-white"
  };
  return <button className={`${base} ${styles[variant]} ${className}`} {...props} />;
}
