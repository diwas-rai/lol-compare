import { useEffect, useMemo, useState } from "react";
import ScatterPlot from "../components/scatter-plot";
import { API_URL } from "../constants/constants";

interface CoordsFromBackend {
  [key: string]: [number, number];
}

interface CoordPoint {
  x: number;
  y: number;
  key: string;
}

export default function Home() {
  const [backendData, setBackendData] = useState<CoordPoint[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/pro-stats/coords/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        const coords = Object.entries(data as CoordsFromBackend).map(
          ([key, [x, y]]) => ({ x, y, key }),
        );
        setBackendData(coords);
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

  const calculateDomain = (data: CoordPoint[]) => {
    return data.reduce(
      (acc, point) => ({
        minX: Math.min(acc.minX, point.x),
        maxX: Math.max(acc.maxX, point.x),
        minY: Math.min(acc.minY, point.y),
        maxY: Math.max(acc.maxY, point.y),
      }),
      {
        minX: data[0]?.x || 0,
        maxX: data[0]?.x || 0,
        minY: data[0]?.y || 0,
        maxY: data[0]?.y || 0,
      },
    );
  };

  const domain = useMemo((): { x: [number, number]; y: [number, number] } => {
    if (!backendData || backendData.length === 0)
      return { x: [0, 0], y: [0, 0] };
    const { minX, maxX, minY, maxY } = calculateDomain(backendData);
    return { x: [minX - 1, maxX + 1], y: [minY - 1, maxY + 1] };
  }, [backendData]);

  return (
    <div className="App">
      {loading && <p>Loading data from backend...</p>}

      {error && <p style={{ color: "red" }}>Error: {error.message}</p>}

      {backendData && (
        <div style={{ width: "500px" }}>
          <h2>Data from Backend:</h2>
          <ScatterPlot domain={domain} data={[]} />
        </div>
      )}
    </div>
  );
}
