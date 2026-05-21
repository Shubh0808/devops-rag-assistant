import { AlertCircle, Bot, Database, RefreshCw, Send, Server, UserRound } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const starterQuestions = [
  "How do I troubleshoot CrashLoopBackOff?",
  "What should I check when API latency is high?",
  "What caused the payment API latency incident?",
  "How can I reduce database CPU saturation?",
];

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Ask me about Kubernetes incidents, API latency, database CPU, or previous incident reports.",
      sources: [],
      modelUsed: "system",
    },
  ]);
  const [question, setQuestion] = useState("");
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);

  const modelLabel = useMemo(() => {
    if (!health?.ollama) {
      return "checking";
    }

    if (health.ollama.available && health.ollama.model_downloaded) {
      return `Ollama ready: ${health.ollama.model}`;
    }

    if (health.ollama.available) {
      return `Ollama running, model missing: ${health.ollama.model}`;
    }

    return "retrieval fallback";
  }, [health]);

  useEffect(() => {
    refreshHealth();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function refreshHealth() {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (!response.ok) {
        throw new Error("Backend health check failed");
      }
      setHealth(await response.json());
      setError("");
    } catch {
      setError("Backend is not reachable. Start FastAPI on http://127.0.0.1:8000.");
    }
  }

  async function ingestDocuments() {
    setIndexing(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/ingest`, { method: "POST" });
      if (!response.ok) {
        throw new Error("Indexing failed");
      }
      await refreshHealth();
    } catch {
      setError("Could not index documents. Check that the backend is running.");
    } finally {
      setIndexing(false);
    }
  }

  async function askQuestion(nextQuestion = question) {
    const cleanQuestion = nextQuestion.trim();
    if (!cleanQuestion || loading) {
      return;
    }

    const userMessage = { role: "user", content: cleanQuestion };
    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: cleanQuestion, top_k: 4 }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          modelUsed: data.model_used,
        },
      ]);
      await refreshHealth();
    } catch {
      setError("The assistant could not answer. Check the backend terminal for details.");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    askQuestion();
  }

  return (
    <main className="app-shell">
      <aside className="side-panel">
        <div className="brand">
          <div className="brand-icon">
            <Bot size={28} aria-hidden="true" />
          </div>
          <div>
            <h1>DevOps RAG Assistant</h1>
            <p>Runbook and incident Q&A</p>
          </div>
        </div>

        <section className="status-grid" aria-label="System status">
          <div className="status-item">
            <Database size={18} aria-hidden="true" />
            <span>{health?.indexed_count ?? 0} chunks indexed</span>
          </div>
          <div className="status-item">
            <Server size={18} aria-hidden="true" />
            <span>{modelLabel}</span>
          </div>
        </section>

        <button className="secondary-button" onClick={ingestDocuments} disabled={indexing}>
          <RefreshCw size={18} aria-hidden="true" className={indexing ? "spin" : ""} />
          <span>{indexing ? "Indexing" : "Re-index documents"}</span>
        </button>

        <section className="question-bank" aria-label="Starter questions">
          <h2>Try Asking</h2>
          {starterQuestions.map((starterQuestion) => (
            <button
              key={starterQuestion}
              className="starter-question"
              onClick={() => askQuestion(starterQuestion)}
              disabled={loading}
            >
              {starterQuestion}
            </button>
          ))}
        </section>
      </aside>

      <section className="chat-panel" aria-label="Chat">
        {error && (
          <div className="error-banner" role="alert">
            <AlertCircle size={18} aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        <div className="messages">
          {messages.map((message, index) => (
            <article key={`${message.role}-${index}`} className={`message ${message.role}`}>
              <div className="avatar" aria-hidden="true">
                {message.role === "assistant" ? <Bot size={18} /> : <UserRound size={18} />}
              </div>
              <div className="bubble">
                <p>{message.content}</p>
                {message.modelUsed && message.modelUsed !== "system" && (
                  <span className="model-pill">{message.modelUsed}</span>
                )}
                {message.sources?.length > 0 && (
                  <div className="sources">
                    <h3>Sources</h3>
                    {message.sources.map((source) => (
                      <div className="source" key={`${source.source}-${source.score}`}>
                        <strong>{source.title}</strong>
                        <span>
                          {source.category} · {source.source} · score {source.score}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}

          {loading && (
            <article className="message assistant">
              <div className="avatar" aria-hidden="true">
                <Bot size={18} />
              </div>
              <div className="bubble loading">Searching runbooks and incidents...</div>
            </article>
          )}
          <div ref={scrollRef} />
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a DevOps incident question..."
            aria-label="Question"
          />
          <button type="submit" disabled={loading || !question.trim()} aria-label="Send question">
            <Send size={20} aria-hidden="true" />
          </button>
        </form>
      </section>
    </main>
  );
}

export default App;

