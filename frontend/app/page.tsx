"use client";

import { useState } from "react";

interface ScoreResponse {
  risk_score: number;
  label: "legit" | "suspect";
  explanation: string;
}

export default function Home() {
  const [title, setTitle] = useState("");
  const [brand, setBrand] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("/api/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          brand,
          price: parseFloat(price),
          description,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data: ScoreResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">CounterCheck</h1>
        <p className="text-gray-600 mb-8">
          Hybrid ML + LLM counterfeit listing detector
        </p>

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Brand
            </label>
            <input
              type="text"
              value={brand}
              onChange={(e) => setBrand(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price (EUR)
            </label>
            <input
              type="number"
              step="0.01"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            {loading ? "Scoring..." : "Score listing"}
          </button>
        </form>

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            Error: {error}
          </div>
        )}

        {result && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-3">
              <span
                className={`inline-block w-3 h-3 rounded-full ${
                  result.label === "suspect" ? "bg-red-500" : "bg-green-500"
                }`}
              />
              <span className="font-semibold text-gray-900 capitalize">
                {result.label}
              </span>
              <span className="text-gray-500 text-sm">
                risk score: {result.risk_score.toFixed(3)}
              </span>
            </div>
            <p className="text-gray-700 whitespace-pre-wrap">{result.explanation}</p>
          </div>
        )}
    
        <footer className="mt-10 text-xs text-gray-500 text-center leading-relaxed space-y-2">
  <p>
    CounterCheck is a portfolio demo. The classifier was trained on 100
    hand-labeled listings and is intended to illustrate a hybrid ML + LLM
    architecture, not as a production tool. Edge cases (especially novel
    digit-substitution patterns and brand spellings outside the training
    set) may be misclassified. See the{" "}
    <a
      href="https://github.com/svanlieshout27-commits/countercheck"
      target="_blank"
      rel="noopener noreferrer"
      className="underline hover:text-gray-700"
    >
      GitHub repo
    </a>{" "}
    for the full methodology and limitations.
  </p>
  <p>
    Built by{" "}
    <a
      href="https://www.linkedin.com/in/sebastiaan-van-lieshout/"
      target="_blank"
      rel="noopener noreferrer"
      className="underline hover:text-gray-700"
    >
      Sebastiaan van Lieshout
    </a>
    {" "}— Brand Protection Specialist transitioning into AI engineering.
  </p>
</footer>
      </div>
    </main>
  );
}