'use client';

import { useEffect, useState } from 'react';

type OOVItem = {
  word: string;
  score: number;
  tag: string;
};

export default function Home() {
  const [items, setItems] = useState<OOVItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/oov')
      .then((res) => res.json())
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch OOV data', err);
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-blue-900 mb-2">Moim Translator Dashboard</h1>
          <p className="text-gray-600">University Christian Community OOV Monitor</p>
        </header>

        <section className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-800">New Word Candidates</h2>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
              Run Analysis
            </button>
          </div>

          {loading ? (
            <p className="text-center py-10 text-gray-500">Loading analysis data...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 text-gray-500 text-sm">
                    <th className="py-3 px-4">Word</th>
                    <th className="py-3 px-4">Score</th>
                    <th className="py-3 px-4">Detected Tag</th>
                    <th className="py-3 px-4">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-blue-50">
                      <td className="py-3 px-4 font-medium text-gray-900">{item.word}</td>
                      <td className="py-3 px-4 text-blue-600 font-mono">{item.score.toFixed(2)}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold
                          ${item.tag === 'Biblical' ? 'bg-purple-100 text-purple-700' :
                            item.tag === 'University' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}`}>
                          {item.tag}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <button className="text-sm text-gray-500 hover:text-blue-600">Verify</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
