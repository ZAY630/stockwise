"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, User, Bot, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { createSSERequest } from "@/lib/api-client";
import { useMarket } from "@/lib/market-context";

interface Message {
  role: "user" | "agent";
  content: string;
  agent?: string;
}

// Shared markdown component styling for tables, headings, etc.
const MarkdownComponents = {
  table: ({ children }: { children: React.ReactNode }) => (
    <div className="my-3 overflow-x-auto rounded-lg border border-gray-700">
      <table className="min-w-full divide-y divide-gray-700 text-xs">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }: { children: React.ReactNode }) => (
    <thead className="bg-gray-800/50">{children}</thead>
  ),
  th: ({ children }: { children: React.ReactNode }) => (
    <th className="px-3 py-2 text-left font-semibold text-blue-300">{children}</th>
  ),
  td: ({ children }: { children: React.ReactNode }) => (
    <td className="px-3 py-1.5 text-gray-200 border-t border-gray-700/50">{children}</td>
  ),
  h2: ({ children }: { children: React.ReactNode }) => (
    <h2 className="mb-2 mt-4 text-base font-semibold text-blue-400">{children}</h2>
  ),
  h3: ({ children }: { children: React.ReactNode }) => (
    <h3 className="mb-1 mt-3 text-sm font-semibold text-white">{children}</h3>
  ),
  strong: ({ children }: { children: React.ReactNode }) => (
    <strong className="font-semibold text-white">{children}</strong>
  ),
  ul: ({ children }: { children: React.ReactNode }) => (
    <ul className="mb-3 space-y-0.5 list-disc list-inside text-gray-300 text-xs">{children}</ul>
  ),
  ol: ({ children }: { children: React.ReactNode }) => (
    <ol className="mb-3 space-y-0.5 list-decimal list-inside text-gray-300 text-xs">{children}</ol>
  ),
  blockquote: ({ children }: { children: React.ReactNode }) => (
    <blockquote className="my-2 border-l-3 border-blue-500/40 pl-3 italic text-gray-400 text-xs">
      {children}
    </blockquote>
  ),
  code: ({ children, className }: { children: React.ReactNode; className?: string }) => {
    const isInline = !className;
    return isInline ? (
      <code className="rounded bg-gray-800 px-1 py-0.5 text-xs text-blue-300 font-mono">
        {children}
      </code>
    ) : (
      <pre className="my-2 overflow-x-auto rounded bg-gray-800/50 p-3 text-xs font-mono">
        <code className={className}>{children}</code>
      </pre>
    );
  },
};

const QUICK_ACTIONS = [
  "What is a P/E ratio?",
  "How do I start investing?",
  "Analyze AAPL for me",
  "What is the S&P 500?",
  "Explain RSI indicator",
];

export default function ChatPage() {
  const { t, market } = useMarket();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingAgent, setStreamingAgent] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Refs to track streaming state without stale closure issues
  const streamingContentRef = useRef("");
  const streamingAgentRef = useRef("");

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const handleSend = async (text?: string) => {
    const query = text || input.trim();
    if (!query || streaming) return;

    const userMsg: Message = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStreaming(true);
    setStreamingContent("");
    setStreamingAgent("");
    streamingContentRef.current = "";
    streamingAgentRef.current = "";

    try {
      const stream = await createSSERequest("/chat", {
        query,
        stream: true,
      });

      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.agent && data.content) {
                streamingAgentRef.current = data.agent;
                streamingContentRef.current += data.content;
                setStreamingAgent(data.agent);
                setStreamingContent(streamingContentRef.current);
              } else if (data.status === "analyzing" && data.agent) {
                const msg = `🔄 ${data.agent} is analyzing...`;
                streamingAgentRef.current = msg;
                setStreamingAgent(msg);
              }
            } catch {
              // Skip malformed data
            }
          } else if (line.startsWith("event: done")) {
            // Finalize using refs (not stale closure state)
            const finalContent = streamingContentRef.current;
            const finalAgent = streamingAgentRef.current;
            if (finalContent) {
              setMessages((prev) => [
                ...prev,
                { role: "agent", content: finalContent, agent: finalAgent || "StockWise" },
              ]);
            }
            streamingContentRef.current = "";
            streamingAgentRef.current = "";
            setStreamingContent("");
            setStreamingAgent("");
          }
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          content: `Sorry, I encountered an error: ${err instanceof Error ? err.message : "Unknown error"}. Please try again.`,
          agent: "System",
        },
      ]);
    } finally {
      setStreaming(false);
      streamingContentRef.current = "";
      streamingAgentRef.current = "";
      setStreamingContent("");
      setStreamingAgent("");
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-800 px-8 py-5">
        <h1 className="text-xl font-bold">
          💬 {market === "cn" ? "AI 智能体对话" : "Chat with AI Agents"}
        </h1>
        <p className="text-sm text-gray-500">{t.chat_desc}</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Sparkles className="mb-4 h-12 w-12 text-blue-400" />
            <h2 className="mb-2 text-xl font-semibold">
              {t.ask_investing}
            </h2>
            <p className="mb-8 max-w-md text-gray-500">
              {market === "cn"
                ? "我可以分析股票、解释金融概念，并给出有据可依的建议——全部用通俗易懂的语言。"
                : "I can analyze stocks, explain financial concepts, and give you reasoned recommendations. All in beginner-friendly language."}
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action}
                  onClick={() => handleSend(action)}
                  className="rounded-full border border-gray-700 px-4 py-2 text-sm text-gray-400 transition hover:border-blue-500/50 hover:text-blue-400"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-6 flex gap-4 ${
              msg.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                msg.role === "user"
                  ? "bg-blue-600"
                  : msg.agent?.includes("News")
                    ? "bg-purple-600"
                    : msg.agent?.includes("Financial")
                      ? "bg-emerald-600"
                      : msg.agent?.includes("Market")
                        ? "bg-amber-600"
                        : "bg-gray-600"
              }`}
            >
              {msg.role === "user" ? (
                <User className="h-4 w-4" />
              ) : (
                <Bot className="h-4 w-4" />
              )}
            </div>
            <div
              className={`max-w-[75%] rounded-xl px-5 py-4 ${
                msg.role === "user"
                  ? "bg-blue-600/20 text-blue-100"
                  : "bg-gray-800/50 text-gray-200"
              }`}
            >
              {msg.agent && (
                <p className="mb-2 text-xs font-medium text-gray-500">
                  {msg.agent}
                </p>
              )}
              <div className="markdown-content prose prose-invert max-w-none text-sm">
                {msg.role === "user" ? (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={MarkdownComponents}
                  >
                    {msg.content}
                  </ReactMarkdown>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Streaming indicator */}
        {streaming && streamingContent && (
          <div className="mb-6 flex gap-4">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-600">
              <Loader2 className="h-4 w-4 animate-spin" />
            </div>
            <div className="max-w-[75%] rounded-xl bg-gray-800/50 px-5 py-4">
              {streamingAgent && (
                <p className="mb-2 text-xs font-medium text-blue-400">
                  {streamingAgent}
                </p>
              )}
              <div className="markdown-content prose prose-invert max-w-none text-sm">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={MarkdownComponents}
                >
                  {streamingContent}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}

        {streaming && !streamingContent && (
          <div className="flex items-center gap-3 py-4 text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">{t.agents_thinking}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-800 px-8 py-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t.type_message}
            className="flex-1 rounded-xl border border-gray-700 bg-gray-800/50 px-5 py-3 text-sm text-white placeholder-gray-500 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
            disabled={streaming}
          />
          <button
            type="submit"
            disabled={!input.trim() || streaming}
            className="rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-500 disabled:opacity-50"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
