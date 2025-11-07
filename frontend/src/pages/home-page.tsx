import { useEffect, useState } from "react";
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

export default function Home() {
  const [backendData, setBackendData] = useState<CoordPoint[] | null>(null);
  const [minX, setMinX] = useState<number>();
  const [minY, setMinY] = useState<number>();
  const [maxX, setMaxX] = useState<number>();
  const [maxY, setMaxY] = useState<number>();
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
        const coords = Object.entries(data as CoordsFromBackend).map(
          ([key, [x, y]]) => ({ x, y, key }),
        );
        setBackendData(coords);
        const allX = coords.map((point) => point.x);
        const allY = coords.map((point) => point.y);

        setMaxX(Math.max(...allX));
        setMaxY(Math.max(...allY));
        setMinX(Math.min(...allX));
        setMinY(Math.min(...allY));
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

  const VictoryZoomVoronoiContainer = createContainer("zoom", "voronoi");

  return (
    <div className="App">
      {loading && <p>Loading data from backend...</p>}

      {error && <p style={{ color: "red" }}>Error: {error.message}</p>}

      {backendData && (
        <div>
          <h2>Data from Backend:</h2>
          {minX !== undefined &&
            maxX !== undefined &&
            minY !== undefined &&
            maxY !== undefined && (
              <VictoryChart
                domain={{ x: [minX - 1, maxX + 1], y: [minY - 1, maxY + 1] }}
                theme={VictoryTheme.material}
                containerComponent={
                  <VictoryZoomVoronoiContainer
                    labels={({ datum }) => datum.key}
                    labelComponent={<VictoryTooltip dy={-10} />}
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
            )}
        </div>
      )}
    </div>
  );
}
