export function ScaleDiverging(key: any, channels: any, options: any): {
    type: any;
    domain: (string | number | undefined)[];
    pivot: number;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    scale: any;
};
export function ScaleDivergingSqrt(key: any, channels: any, options: any): {
    type: any;
    domain: (string | number | undefined)[];
    pivot: number;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    scale: any;
};
export function ScaleDivergingPow(key: any, channels: any, { exponent, ...options }: {
    [x: string]: any;
    exponent?: number | undefined;
}): {
    type: any;
    domain: (string | number | undefined)[];
    pivot: number;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    scale: any;
};
export function ScaleDivergingLog(key: any, channels: any, { base, pivot, domain, ...options }: {
    [x: string]: any;
    base?: number | undefined;
    pivot?: number | undefined;
    domain?: number[] | (string | undefined)[] | undefined;
}): {
    type: any;
    domain: (string | number | undefined)[];
    pivot: number;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    scale: any;
};
export function ScaleDivergingSymlog(key: any, channels: any, { constant, ...options }: {
    [x: string]: any;
    constant?: number | undefined;
}): {
    type: any;
    domain: (string | number | undefined)[];
    pivot: number;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    scale: any;
};
import { interpolateNumber } from "d3-interpolate";
