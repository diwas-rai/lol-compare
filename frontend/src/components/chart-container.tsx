import { AlertCircle, RotateCcw } from "lucide-react";
import { useRef } from "react";
import type { ChartDomain, ScatterPoint } from "../types";
import ScatterPlot, { type ScatterPlotRef } from "./echarts-scatter";

interface ScatterPlotContainerProps {
  data: ScatterPoint[];
  domain: ChartDomain;
  isPlayerAnalysisLoading: boolean;
  playerAnalysisError: Error | null;
}

export default function ScatterPlotContainer({
  data,
  domain,
  isPlayerAnalysisLoading,
  playerAnalysisError,
}: ScatterPlotContainerProps) {
  const chartRef = useRef<ScatterPlotRef>(null);

  return (
    <div className="relative flex min-h-[500px] items-center justify-center overflow-hidden rounded-3xl border border-white/5 bg-slate-900/50 p-8 shadow-2xl">
      <div className="absolute top-4 right-6 z-30 flex flex-col items-end gap-2">
        <div className="pointer-events-none flex animate-pulse items-center gap-2 rounded-full border border-white/10 bg-black/60 px-3 py-1 text-xs text-white shadow-lg select-none">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
            <path
              d="M12 5v14M12 19l-3-3m3 3l3-3M12 5l-3 3m3-3l3 3"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span className="opacity-80">Scroll to zoom</span>
        </div>

        {!isPlayerAnalysisLoading && !playerAnalysisError && (
          <button
            onClick={() => chartRef.current?.resetZoom()}
            className="flex items-center gap-2 rounded-full border border-indigo-400/20 bg-indigo-600 px-3 py-1.5 text-xs text-white shadow-lg transition-colors duration-200 hover:bg-indigo-500"
          >
            <RotateCcw size={14} />
            Reset View
          </button>
        )}
      </div>

      {isPlayerAnalysisLoading && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-slate-900/80 backdrop-blur-sm">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
          <span className="animate-pulse text-sm text-slate-400">
            Fetching player stats and analysing...
          </span>
        </div>
      )}

      {playerAnalysisError && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-slate-900/90 text-red-400">
          <AlertCircle size={32} />
          <span>{playerAnalysisError.message}</span>
        </div>
      )}

      <div className="relative z-10 flex h-full w-full items-center justify-center">
        <div className="aspect-square h-full w-full max-w-[700px]">
          <ScatterPlot ref={chartRef} data={data} domain={domain} />
        </div>
      </div>
    </div>
  );
}
