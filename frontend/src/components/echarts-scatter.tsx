import * as echarts from "echarts";
import ReactECharts from "echarts-for-react";
import type { CallbackDataParams } from "echarts/types/dist/shared";
import { useMemo } from "react";

export interface ScatterPoint {
  x: number;
  y: number;
  key: string;
  fill: string;
}

interface ScatterPlotProps {
  data: ScatterPoint[];
  domain: {
    x: [number, number];
    y: [number, number];
  };
}

interface ScatterSeriesData {
  value: [number, number];
  key: string;
  itemStyle: { color: string };
}

export default function ScatterPlot({ data, domain }: ScatterPlotProps) {
  const scatterData = useMemo(
    () =>
      data.map((p) => ({
        value: [p.x, p.y],
        key: p.key,
        itemStyle: { color: p.fill },
      })),
    [data],
  );

  const option = useMemo(
    () => ({
      animation: false,
      grid: {
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        containLabel: false,
      },
      xAxis: {
        show: false,
        type: "value",
        min: domain.x[0],
        max: domain.x[1],
      },
      yAxis: {
        show: false,
        type: "value",
        min: domain.y[0],
        max: domain.y[1],
      },
      tooltip: {
        trigger: "item",
        formatter: (params: CallbackDataParams) => {
          const data = params.data as ScatterSeriesData;
          return data.key;
        },
        backgroundColor: "rgba(0,0,0,0.8)",
        borderColor: "#333",
        textStyle: { color: "#fff" },
      },
      dataZoom: [
        {
          type: "inside",
          xAxisIndex: 0,
          yAxisIndex: 0,
          zoomOnMouseWheelCenter: "pointer",
          zoomOnMouseWheel: true,
          moveOnMouseWheel: false,
          moveOnMouseMove: true,
          filterMode: "none",
        },
      ],
      series: [
        {
          type: "scatter",
          symbolSize: 8,
          data: scatterData,
          large: true,
        },
      ],
    }),
    [scatterData, domain],
  );

  return (
    <ReactECharts
      option={option}
      echarts={echarts}
      notMerge={true}
      lazyUpdate={true}
      style={{ width: "100%", height: "100%" }}
    />
  );
}
