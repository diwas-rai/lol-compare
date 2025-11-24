import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, AlertCircle, ChevronDown, Search, X } from "lucide-react";
import { useState } from "react";
import ScatterPlot from "../components/scatter-plot";
import { API_URL } from "../constants/constants";
import { useChartDomain } from "../hooks/useChartDomain";

interface CoordsFromBackend {
  [key: string]: [number, number];
}

const REGIONS = ["EUW", "EUNE", "NA", "KR", "JP"];

export default function Home() {
  const queryClient = useQueryClient();
  const [regionInput, setRegionInput] = useState(REGIONS[0]);
  const [riotIdInput, setRiotIdInput] = useState("");
  const [taglineInput, setTaglineInput] = useState("");

  const [searchParams, setSearchParams] = useState<{
    region: string;
    id: string;
    tag: string;
  } | null>(null);

  const { data: proData } = useQuery({
    queryKey: ["pro-data-points"],
    queryFn: async () => {
      const res = await fetch(`${API_URL}api/pro-stats/coords`);
      return await res.json();
    },
    refetchOnWindowFocus: false,
    staleTime: Infinity,
  });

  const {
    data: playerAnalysisData,
    isLoading: isPlayerAnalysisLoading,
    isSuccess: isPlayerAnalysisSuccess,
    error: playerAnalysisError,
  } = useQuery<CoordsFromBackend>({
    queryKey: [
      "player-stats",
      searchParams?.region,
      searchParams?.id,
      searchParams?.tag,
    ],
    queryFn: async ({ queryKey, signal }) => {
      const [, region, id, tag] = queryKey;
      const res = await fetch(
        `${API_URL}api/analyse/?region=${region}&gameName=${id}&tagLine=${tag}`,
        { signal },
      );
      if (!res.ok) throw new Error("Player not found");
      return await res.json();
    },
    enabled:
      !!searchParams?.region && !!searchParams?.id && !!searchParams?.tag,
    refetchOnWindowFocus: false,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();

    if (isPlayerAnalysisLoading) {
      queryClient.cancelQueries({ queryKey: ["player-stats"] });
      return;
    }

    if (riotIdInput && taglineInput) {
      setSearchParams({
        region: regionInput,
        id: riotIdInput,
        tag: taglineInput,
      });
    }
  };

  const proCoords = proData
    ? Object.entries(proData as CoordsFromBackend).map(([key, [x, y]]) => ({
        x,
        y,
        key,
        fill: "#5C6BC0", //indigo-400
      }))
    : [];

  const playerCoords = playerAnalysisData
    ? Object.entries(playerAnalysisData).map(([key, [x, y]]) => ({
        x,
        y,
        key,
        fill: "4dd0e1", //cyan-300
      }))
    : [];

  const allCoords = playerCoords
    ? [...proCoords, ...playerCoords]
    : [...proCoords];
  const domain = useChartDomain(allCoords);

  return (
    <div className="min-h-screen bg-neutral-950 text-slate-200 selection:bg-indigo-500/30 flex flex-col items-center py-20 px-4 relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-indigo-900/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[600px] h-[400px] bg-slate-800/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="w-full max-w-4xl z-10 space-y-12">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold tracking-tight text-white drop-shadow-lg">
            LoL{" "}
            <span className="text-transparent bg-clip-text bg-linear-to-r from-indigo-400 to-cyan-300">
              Compare
            </span>
          </h1>
          <p className="text-slate-400 text-lg max-w-lg mx-auto">
            Analyse player mechanics and positioning against professional
            datasets.
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 shadow-2xl">
          <form
            onSubmit={handleSearch}
            className="flex flex-col md:flex-row gap-4 items-end"
          >
            <div className="w-full md:w-32 space-y-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 ml-1">
                Region
              </label>
              <div className="relative">
                <select
                  value={regionInput}
                  onChange={(e) => setRegionInput(e.target.value)}
                  className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 appearance-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white transition-all cursor-pointer"
                >
                  {REGIONS.map((region) => (
                    <option
                      key={region}
                      value={region}
                      className="bg-slate-900"
                    >
                      {region}
                    </option>
                  ))}
                </select>
                <ChevronDown
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none"
                  size={16}
                />
              </div>
            </div>

            <div className="flex-1 space-y-2 w-full">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 ml-1">
                Riot ID
              </label>
              <input
                type="text"
                placeholder="Faker"
                value={riotIdInput}
                onChange={(e) => setRiotIdInput(e.target.value)}
                className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white placeholder:text-slate-600 transition-all"
              />
            </div>

            <div className="flex-[0.5] space-y-2 w-full md:w-auto">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 ml-1">
                Tagline
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                  #
                </span>
                <input
                  type="text"
                  placeholder="KR1"
                  value={taglineInput}
                  onChange={(e) => setTaglineInput(e.target.value)}
                  className="w-full bg-black/20 border border-white/10 rounded-xl pl-8 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white placeholder:text-slate-600 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              className={`cursor-pointer w-full md:w-auto font-medium py-3 px-8 rounded-xl transition-all shadow-[0_0_20px_-5px_rgba(79,70,229,0.5)] flex items-center justify-center gap-2 ${
                isPlayerAnalysisLoading
                  ? "bg-red-500/80 hover:bg-red-500 text-white"
                  : "bg-indigo-600 hover:bg-indigo-500 text-white"
              }`}
            >
              {isPlayerAnalysisLoading ? (
                <>
                  <X size={18} />
                  <span>Cancel</span>
                </>
              ) : (
                <>
                  <Search size={18} />
                  <span>Analyse</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Chart Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between px-2">
            <h2 className="flex items-center gap-2 text-xl font-medium text-white">
              <Activity size={20} className="text-indigo-400" />
              Comparison Chart
            </h2>
            {isPlayerAnalysisSuccess && searchParams && (
              <span className="text-xs px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Showing: {searchParams.id}#{searchParams.tag}
              </span>
            )}
          </div>

          <div className="relative bg-slate-900/50 border border-white/5 rounded-3xl p-8 shadow-2xl overflow-hidden min-h-[500px] flex items-center justify-center">
            {/* Zoom hint overlay */}
            <div className="absolute top-4 right-6 z-30 flex items-center gap-2 bg-black/60 text-white text-xs px-3 py-1 rounded-full shadow-lg animate-pulse pointer-events-none select-none">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                <path
                  d="M12 5v14M12 19l-3-3m3 3l3-3M12 5l-3 3m3-3l3 3"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Scroll/Pinch to zoom
            </div>

            {isPlayerAnalysisLoading && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-900/80 backdrop-blur-sm z-20">
                <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-slate-400 text-sm animate-pulse">
                  Fetching player stats and analysing...
                </span>
              </div>
            )}

            {playerAnalysisError && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-900/90 z-20 text-red-400">
                <AlertCircle size={32} />
                <span>{playerAnalysisError.message}</span>
              </div>
            )}

            <div className="w-full h-full flex justify-center items-center relative z-10">
              <div className="w-full h-full max-w-[700px] aspect-square">
                <ScatterPlot domain={domain} data={allCoords} />
              </div>
            </div>

            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-size-[40px_40px] mask-[radial-gradient(ellipse_at_center,black,transparent_80%)] pointer-events-none" />
          </div>
        </div>
      </div>
    </div>
  );
}
