export interface ScatterPoint {
  x: number;
  y: number;
  key: string;
  fill: string;
}

export interface ChartDomain {
  x: [min: number, max: number];
  y: [min: number, max: number];
}

export enum REGIONS {
  EUW = "EUW",
  EUNE = "EUNE",
  NA = "NA",
  KR = "KR",
  JP = "JP",
}
