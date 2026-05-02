"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Boxes, ClipboardList, LayoutDashboard, UserRound } from "lucide-react";
import { ReactNode } from "react";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/account", label: "账号基准", icon: UserRound },
  { href: "/assets", label: "素材库", icon: Boxes },
  { href: "/publish", label: "发布矩阵", icon: ClipboardList },
  { href: "/review", label: "内容实验复盘", icon: BarChart3 }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-surface">
      <aside className="fixed left-0 top-0 hidden h-screen w-64 border-r border-line bg-white p-5 md:block">
        <div className="mb-8">
          <div className="text-xl font-semibold text-ink">LiveMark</div>
          <div className="mt-1 text-xs text-muted">小红书直拍 KOC 增长资产管理</div>
        </div>
        <nav className="grid gap-1">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm ${active ? "bg-[#fbe8ec] text-brand" : "text-muted hover:bg-surface hover:text-ink"}`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="md:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-6 md:px-8">{children}</div>
      </main>
    </div>
  );
}
