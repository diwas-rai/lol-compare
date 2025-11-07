import { useEffect, useMemo, useState } from "react";
import {
  createContainer,
  VictoryAxis,
  VictoryChart,
  VictoryScatter,
  VictoryTheme,
  VictoryTooltip,
} from "victory";

interface CoordsFromBackend {
  [key: string]: [number, number];
}

interface CoordPoint {
  x: number;
  y: number;
  key: string;
}

const VictoryZoomVoronoiContainer = createContainer("zoom", "voronoi");

export default function Home() {
  const [backendData, setBackendData] = useState<CoordPoint[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch("/api/pro-stats/coords/")
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
          <VictoryChart
            domain={domain}
            theme={VictoryTheme.material}
            containerComponent={
              <VictoryZoomVoronoiContainer
                labels={({ datum }) => datum.key}
                labelComponent={<VictoryTooltip dy={-10} />}
                radius={7}
              />
            }
          >
            <VictoryAxis
              style={{
                grid: { strokeOpacity: 0 },
                axis: { strokeOpacity: 0 },
                axisLabel: { strokeOpacity: 0 },
                tickLabels: { fillOpacity: 0 },
                ticks: { strokeOpacity: 0 },
              }}
            />

            <VictoryScatter
              size={7}
              data={backendData}
              style={{ data: { opacity: 0.5 } }}
            />
          </VictoryChart>
        </div>
      )}
    </div>
  );
}
