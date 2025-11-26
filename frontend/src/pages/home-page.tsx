import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, ChevronDown, Search, X } from "lucide-react";
import { useState } from "react";
import ScatterPlotContainer from "../components/chart-container";
import { API_URL } from "../constants/constants";
import { useChartDomain } from "../hooks/useChartDomain";
import { REGIONS } from "../types";

interface CoordsFromBackend {
  [key: string]: [number, number];
}

export default function Home() {
  const queryClient = useQueryClient();
  const [regionInput, setRegionInput] = useState<REGIONS>(REGIONS.EUW);
  const [riotIdInput, setRiotIdInput] = useState("");
  const [taglineInput, setTaglineInput] = useState("");

  const [searchParams, setSearchParams] = useState<{
    region: REGIONS;
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
        fill: "#4DD0E1", //cyan-300
      }))
    : [];

  const allCoords = playerCoords
    ? [...proCoords, ...playerCoords]
    : [...proCoords];
  const domain = useChartDomain(allCoords);

  return (
    <div className="relative flex min-h-screen flex-col items-center overflow-hidden bg-neutral-950 px-4 py-20 text-slate-200 selection:bg-indigo-500/30">
      {/* Background Ambience */}
      <div className="pointer-events-none absolute top-0 left-1/2 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-indigo-900/20 blur-[120px]" />
      <div className="pointer-events-none absolute right-0 bottom-0 h-[400px] w-[600px] rounded-full bg-slate-800/10 blur-[100px]" />

      <div className="z-10 w-full max-w-4xl space-y-12">
        <div className="space-y-4 text-center">
          <h1 className="text-5xl font-bold tracking-tight text-white drop-shadow-lg">
            LoL{" "}
            <span className="bg-linear-to-r from-indigo-400 to-cyan-300 bg-clip-text text-transparent">
              Compare
            </span>
          </h1>
          <p className="mx-auto max-w-lg text-lg text-slate-400">
            Analyse player mechanics and positioning against professional
            datasets.
          </p>
        </div>

        {/* Search Section */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-lg">
          <form
            onSubmit={handleSearch}
            className="flex flex-col items-end gap-4 md:flex-row"
          >
            <div className="w-full space-y-2 md:w-32">
              <label className="ml-1 text-xs font-semibold tracking-wider text-slate-500 uppercase">
                Region
              </label>
              <div className="relative">
                <select
                  value={regionInput}
                  onChange={(e) => setRegionInput(e.target.value as REGIONS)}
                  className="w-full cursor-pointer appearance-none rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-white transition-all focus:ring-2 focus:ring-indigo-500/50 focus:outline-none"
                >
                  {Object.values(REGIONS).map((region) => (
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
                  className="pointer-events-none absolute top-1/2 right-4 -translate-y-1/2 text-slate-500"
                  size={16}
                />
              </div>
            </div>

            <div className="w-full flex-1 space-y-2">
              <label className="ml-1 text-xs font-semibold tracking-wider text-slate-500 uppercase">
                Riot ID
              </label>
              <input
                type="text"
                placeholder="Faker"
                value={riotIdInput}
                onChange={(e) => setRiotIdInput(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-white transition-all placeholder:text-slate-600 focus:ring-2 focus:ring-indigo-500/50 focus:outline-none"
              />
            </div>

            <div className="w-full flex-[0.5] space-y-2 md:w-auto">
              <label className="ml-1 text-xs font-semibold tracking-wider text-slate-500 uppercase">
                Tagline
              </label>
              <div className="relative">
                <span className="absolute top-1/2 left-4 -translate-y-1/2 text-slate-500">
                  #
                </span>
                <input
                  type="text"
                  placeholder="KR1"
                  value={taglineInput}
                  onChange={(e) => setTaglineInput(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-black/20 py-3 pr-4 pl-8 text-white transition-all placeholder:text-slate-600 focus:ring-2 focus:ring-indigo-500/50 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              className={`flex w-full cursor-pointer items-center justify-center gap-2 rounded-xl px-8 py-3 font-medium shadow-[0_0_20px_-5px_rgba(79,70,229,0.5)] transition-all md:w-auto ${
                isPlayerAnalysisLoading
                  ? "bg-red-500/80 text-white hover:bg-red-500"
                  : "bg-indigo-600 text-white hover:bg-indigo-500"
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
              <span className="rounded-full border border-indigo-500/20 bg-indigo-500/10 px-3 py-1 text-xs text-indigo-400">
                Showing: {searchParams.id}#{searchParams.tag}
              </span>
            )}
          </div>

          <ScatterPlotContainer
            data={allCoords}
            domain={domain}
            isPlayerAnalysisLoading={isPlayerAnalysisLoading}
            playerAnalysisError={playerAnalysisError}
          />

          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] mask-[radial-gradient(ellipse_at_center,black,transparent_80%)] bg-size-[40px_40px]" />
        </div>
      </div>
    </div>
  );
}
