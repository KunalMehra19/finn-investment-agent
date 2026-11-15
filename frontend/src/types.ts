export type Company = {
  ticker: string;
  name: string;
  short: string;
  sector: string;
  color: string;
  initials: string;
  deep: boolean;
};
export type Source = {
  id: string;
  ticker: string;
  title: string;
  kind: string;
  period: string;
  published: string | null;
  url: string;
  pages: number;
  page: number;
  excerpt: string;
  status: string;
  sha256: string;
  retrieved_at: string;
};
export type Price = {
  close: number;
  move: number;
  volume: number;
  relative_volume: number | null;
  as_of: string;
  provider: string;
  basis: string;
  history: { date: string; close: number; volume: number }[];
};
export type Fact = {
  label: string;
  value: string;
  period: string;
  source_id: string;
  page: number;
};
export type Insight = {
  title: string;
  text: string;
  source_id: string;
  page: number;
  tags: string;
  calculation?: string;
  related_source?: string;
};
export type Story = {
  id: string;
  ticker: string;
  display_title: string;
  title: string;
  summary: string;
  why: string;
  source_id: string;
  page: number;
  published: string;
  category: string;
  priority: number;
  origin: string;
  routine: boolean;
};
export type Ledger = {
  id: string;
  ticker: string;
  metric: string;
  period: string;
  status: string;
  promise: string;
  speaker: string;
  date: string;
  target: string;
  actual: string;
  previous: string;
  delta: number | null;
  delta_label: string;
  explanation: string;
  promise_source: string;
  promise_page: number;
  actual_source: string;
  actual_page: number;
  calculation: string;
};
export type Dataset = {
  companies: Company[];
  sources: Source[];
  stories: Story[];
  current_stories?: Story[];
  filing_coverage?: {
    status: string;
    from?: string;
    to?: string;
    checked_at?: string;
    metadata_count?: number;
    verified_count?: number;
  };
  facts: Record<string, Fact[]>;
  insights: Record<string, Insight[]>;
  ledger: Ledger[];
  market: {
    prices: Record<string, Price>;
    status: string;
    fetched_at?: string;
    error?: string;
  };
  coverage: {
    filings: string;
    deep_companies: number;
    documents: number;
    as_of: string;
  };
};
export type Answer = {
  conclusion: string;
  insights: Insight[];
  unknowns: string[];
  engine: string;
  status: string;
  sources?: Source[];
};
