"use client";

import { useState } from "react";
import { Plus, Trash2, TrendingUp, TrendingDown } from "lucide-react";

interface WatchlistItem {
  id: string;
  symbol: string;
  notes: string;
}

export default function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [newSymbol, setNewSymbol] = useState("");
  const [newNotes, setNewNotes] = useState("");

  const addItem = () => {
    if (!newSymbol.trim()) return;
    setItems((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        symbol: newSymbol.trim().toUpperCase(),
        notes: newNotes.trim(),
      },
    ]);
    setNewSymbol("");
    setNewNotes("");
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="mx-auto max-w-4xl px-8 py-10">
      <div className="mb-10">
        <h1 className="mb-2 text-3xl font-bold">My Watchlist</h1>
        <p className="text-gray-400">
          Track stocks you&apos;re interested in. Full watchlist sync coming in
          Phase 3.
        </p>
      </div>

      {/* Add form */}
      <div className="mb-8 flex gap-3">
        <input
          type="text"
          value={newSymbol}
          onChange={(e) => setNewSymbol(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addItem()}
          placeholder="Ticker symbol (e.g., AAPL)"
          className="w-48 rounded-xl border border-gray-700 bg-gray-800/50 px-4 py-3 text-sm text-white placeholder-gray-500 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
        />
        <input
          type="text"
          value={newNotes}
          onChange={(e) => setNewNotes(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && addItem()}
          placeholder="Notes (optional)"
          className="flex-1 rounded-xl border border-gray-700 bg-gray-800/50 px-4 py-3 text-sm text-white placeholder-gray-500 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
        />
        <button
          onClick={addItem}
          className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-500"
        >
          <Plus className="h-4 w-4" /> Add
        </button>
      </div>

      {/* List */}
      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <p className="mb-2 text-lg text-gray-500">
            Your watchlist is empty
          </p>
          <p className="text-sm text-gray-600">
            Add stocks above to start tracking them
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-4 rounded-xl border border-gray-800 bg-gray-900/50 px-5 py-4"
            >
              <a
                href={`/dashboard/stock/${item.symbol}`}
                className="text-lg font-bold text-blue-400 hover:underline"
              >
                {item.symbol}
              </a>
              {item.notes && (
                <span className="text-sm text-gray-500">{item.notes}</span>
              )}
              <div className="flex-1" />
              <button
                onClick={() => removeItem(item.id)}
                className="rounded-lg p-2 text-gray-600 transition hover:bg-red-500/10 hover:text-red-400"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
