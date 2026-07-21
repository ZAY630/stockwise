"use client";

import { MarketProvider } from "@/lib/market-context";
import type { ReactNode } from "react";

export default function Providers({ children }: { children: ReactNode }) {
  return <MarketProvider>{children}</MarketProvider>;
}
