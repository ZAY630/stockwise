"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  List,
  MessageSquare,
  BookOpen,
  TrendingUp,
  ArrowLeft,
} from "lucide-react";
import { useMarket } from "@/lib/market-context";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { t, market, currencySymbol } = useMarket();

  const navItems = [
    { href: "/dashboard", label: t.overview, icon: LayoutDashboard },
    { href: "/dashboard/watchlist", label: t.watchlist, icon: List },
    { href: "/dashboard/chat", label: t.chat, icon: MessageSquare },
    { href: "/dashboard/learn", label: t.learn, icon: BookOpen },
  ];

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col border-r border-gray-800 bg-gray-900/50">
        <div className="flex items-center gap-3 border-b border-gray-800 px-6 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <Link href="/dashboard" className="text-lg font-bold">
            StockWise
          </Link>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" &&
                pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-gray-800 p-4">
          <p className="text-xs text-gray-600">StockWise v0.1.0</p>
          <p className="text-xs text-gray-600">For educational purposes only</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-gray-950">
        {/* Top bar: back button + market indicator */}
        <div className="flex items-center justify-between border-b border-gray-800 px-6 py-3">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-gray-400 transition hover:text-gray-200"
          >
            <ArrowLeft className="h-4 w-4" />
            {market === "cn" ? "返回首页" : "Back to Home"}
          </Link>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{market === "cn" ? "🇨🇳" : "🇺🇸"}</span>
            <span>
              {market === "cn" ? "中国A股" : "US Market"} · {currencySymbol}
            </span>
          </div>
        </div>
        {children}
      </main>
    </div>
  );
}
