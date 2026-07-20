export interface StockInfo {
  symbol: string;
  name: string;
  sector: string;
  industry: string;
  market_cap: number | null;
  description: string;
  website: string;
}

export interface PriceData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  previous_close: number;
  open: number;
  day_high: number;
  day_low: number;
  volume: number;
  fifty_two_week_high: number;
  fifty_two_week_low: number;
}

export interface OHLCVPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface AnalysisResponse {
  symbol: string;
  agent: string;
  analysis: string;
}

export interface ChatMessage {
  role: string;
  content: string;
  agent?: string;
  symbol?: string;
}

export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}
