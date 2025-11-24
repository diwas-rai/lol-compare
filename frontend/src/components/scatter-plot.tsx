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
  return (
    <div style={{ touchAction: "none" }}>
      <VictoryChart
        domain={domain}
        theme={VictoryTheme.material}
        containerComponent={
          <VictoryZoomVoronoiContainer
            labels={({ datum }) => datum.key}
            labelComponent={<VictoryTooltip />}
            radius={dataPointSize}
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
    </div>
  );
}
