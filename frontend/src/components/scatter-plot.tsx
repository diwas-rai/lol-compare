import { useEffect, useRef, useState } from "react";
import {
  VictoryAxis,
  VictoryChart,
  VictoryScatter,
  VictoryTheme,
  VictoryTooltip,
  createContainer,
  type DomainTuple,
  type ForAxes,
} from "victory";

interface GraphProps {
  domain: ForAxes<DomainTuple>;
  data: readonly unknown[];
}

const VictoryZoomVoronoiContainer = createContainer("zoom", "voronoi");
const dataPointSize = 7;

export default function ScatterPlot({ domain, data }: GraphProps) {
  // Setup a reference and state to track the container size
  const ref = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const observeTarget = ref.current;
    if (!observeTarget) return;

    const resizeObserver = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0) return;
      const { width, height } = entries[0].contentRect;
      setSize({ width, height });
    });

    resizeObserver.observe(observeTarget);
    return () => {
      if (observeTarget) resizeObserver.unobserve(observeTarget);
    };
  }, []);

  return (
    <div ref={ref} className="w-full h-full" style={{ touchAction: "none" }}>
      {size.width > 0 && (
        <VictoryChart
          width={size.width}
          height={size.height}
          domain={domain}
          theme={VictoryTheme.material}
          containerComponent={
            <VictoryZoomVoronoiContainer
              labels={({ datum }) => datum.key}
              labelComponent={<VictoryTooltip />}
              radius={dataPointSize}
              allowZoom={true}
              allowPan={true}
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
            size={dataPointSize}
            data={data}
            style={{ data: { opacity: 0.7, fill: ({ datum }) => datum.fill } }}
          />
        </VictoryChart>
      )}
    </div>
  );
}
