import { useMemo } from "react";

interface CoordPoint {
  x: number;
  y: number;
  key: string;
}

const calculateDomain = (data: CoordPoint[]) => {
  if (!data || data.length === 0) {
    return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
  }

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

export const useChartDomain = (coords: CoordPoint[]) => {
  const domain = useMemo((): { x: [number, number]; y: [number, number] } => {
    if (!coords || coords.length === 0) return { x: [0, 0], y: [0, 0] };

    const { minX, maxX, minY, maxY } = calculateDomain(coords);

    return { x: [minX - 1, maxX + 1], y: [minY - 1, maxY + 1] };
  }, [coords]);

  return domain;
};
