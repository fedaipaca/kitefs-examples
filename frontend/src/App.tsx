import { useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const TOWNS = [
  { id: 1, name: "Kadikoy (Istanbul)" },
  { id: 2, name: "Besiktas (Istanbul)" },
  { id: 3, name: "Tuzla (Istanbul)" },
  { id: 4, name: "Cankaya (Ankara)" },
  { id: 5, name: "Kecioren (Ankara)" },
  { id: 6, name: "Mamak (Ankara)" },
];

function App() {
  const [townId, setTownId] = useState(1);
  const [netArea, setNetArea] = useState("");
  const [rooms, setRooms] = useState("");
  const [buildYear, setBuildYear] = useState("");
  const [loading, setLoading] = useState(false);
  const [price, setPrice] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setPrice(null);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/recommend-price`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          town_id: townId,
          net_area: Number(netArea),
          number_of_rooms: Number(rooms),
          build_year: Number(buildYear),
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(data.detail ?? `Request failed (${res.status})`);
        return;
      }

      const data = await res.json();
      setPrice(data.recommended_price);
    } catch {
      setError("Could not reach the backend. Is it running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>House Price Estimator</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Town
          <select value={townId} onChange={(e) => setTownId(Number(e.target.value))}>
            {TOWNS.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Net Area (m²)
          <input type="number" min={1} required value={netArea} onChange={(e) => setNetArea(e.target.value)} />
        </label>

        <label>
          Number of Rooms
          <input type="number" min={1} required value={rooms} onChange={(e) => setRooms(e.target.value)} />
        </label>

        <label>
          Build Year
          <input
            type="number"
            min={1900}
            max={2030}
            required
            value={buildYear}
            onChange={(e) => setBuildYear(e.target.value)}
          />
        </label>

        <div className="submit-row">
          <button type="submit" disabled={loading}>
            {loading ? "Getting estimate…" : "Get Price Estimate"}
          </button>
          {loading && <span className="status">Loading…</span>}
          {price !== null && !loading && (
            <span className="result">
              Estimated price: <strong>{price.toLocaleString("tr-TR")} TRY</strong>
            </span>
          )}
          {error && !loading && <span className="error">{error}</span>}
        </div>
      </form>
    </div>
  );
}

export default App;
