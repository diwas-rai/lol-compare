import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
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
  const { isPending, error, data } = useQuery({
    queryKey: ["pro-data-points"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/pro-stats/coords`);
      return await res.json();
    },
  });

  const coords = Object.entries(data as CoordsFromBackend).map(
    ([key, [x, y]]) => ({ x, y, key }),
  );

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
    if (!coords || coords.length === 0) return { x: [0, 0], y: [0, 0] };
    const { minX, maxX, minY, maxY } = calculateDomain(coords);
    return { x: [minX - 1, maxX + 1], y: [minY - 1, maxY + 1] };
  }, [coords]);

  return (
    <div className="App">
      {isPending && "Loading..."}
      {error && "An error has occurred: " + error.message}

      <div style={{ width: "500px" }}>
        <h2>Data from Backend:</h2>
        <ScatterPlot domain={domain} data={coords} />
      </div>
    </div>
  );
}
