import { useEffect, useState } from "react";
import reactLogo from "../assets/react.svg";

export default function Home() {
  const [backendData, setBackendData] = useState(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BASE_URL}/api/pro-stats/coords/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        setBackendData(data);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (err instanceof Error) {
          setError(err);
        } else {
          setError(new Error("An unknown error occurred."));
        }
        setLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <div>
        <a href="https://reactjs.org" target="_blank" rel="noreferrer">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React + Bun ⚡ (TypeScript)</h1>
      <hr />

      <div className="card">
        {loading && <p>Loading data from backend...</p>}

        {error && <p style={{ color: "red" }}>Error: {error.message}</p>}

        {backendData && (
          <div>
            <h2>Data from Backend:</h2>
            <pre
              style={{
                textAlign: "left",
                backgroundColor: "#f0f0f0",
                color: "#333",
                padding: "10px",
                borderRadius: "5px",
              }}
            >
              {JSON.stringify(backendData, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
