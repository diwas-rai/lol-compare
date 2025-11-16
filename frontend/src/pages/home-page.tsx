import { useQuery } from "@tanstack/react-query";
import ScatterPlot from "../components/scatter-plot";
import { API_URL } from "../constants/constants";
import { useChartDomain } from "../hooks/useChartDomain";

interface CoordsFromBackend {
  [key: string]: [number, number];
}

export default function Home() {
  const { isPending, error, data } = useQuery({
    queryKey: ["pro-data-points"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/api/pro-stats/coords`);
      return await res.json();
    },
  });

  const coords = data
    ? Object.entries(data as CoordsFromBackend).map(([key, [x, y]]) => ({
        x,
        y,
        key,
      }))
    : undefined;

  const domain = useChartDomain(coords ?? []);

  return (
    <div className="App">
      {isPending && "Loading..."}
      {error && "An error has occurred: " + error.message}

      <div style={{ width: "500px" }}>
        <h2>Data from Backend:</h2>
        <ScatterPlot domain={domain} data={coords ?? []} />
      </div>
    </div>
  );
}
