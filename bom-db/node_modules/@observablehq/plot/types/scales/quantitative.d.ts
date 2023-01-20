export function Interpolator(interpolate: any): typeof interpolateNumber | undefined;
export function ScaleQ(key: any, scale: any, channels: any, { type, nice, clamp, zero, domain, unknown, round, scheme, interval, range, interpolate, reverse }: {
    type: any;
    nice: any;
    clamp: any;
    zero: any;
    domain?: (string | number | undefined)[] | undefined;
    unknown: any;
    round: any;
    scheme: any;
    interval: any;
    range?: any;
    interpolate?: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    reverse: any;
}): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    interval: any;
};
export function ScaleLinear(key: any, channels: any, options: any): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    interval: any;
};
export function ScaleSqrt(key: any, channels: any, options: any): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    interval: any;
};
export function ScalePow(key: any, channels: any, { exponent, ...options }: {
    [x: string]: any;
    exponent?: number | undefined;
}): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    interval: any;
};
export function ScaleLog(key: any, channels: any, { base, domain, ...options }: {
    [x: string]: any;
    base?: number | undefined;
    domain?: number[] | (string | undefined)[] | undefined;
}): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    interval: any;
};
export function ScaleSymlog(key: any, channels: any, { constant, ...options }: {
    [x: string]: any;
    constant?: number | undefined;
}): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    interpolate: import("d3-interpolate").ColorGammaInterpolationFactory | ((t: number) => string) | typeof interpolateNumber | undefined;
    interval: any;
};
export function ScaleQuantile(key: any, channels: any, { range, quantiles, n, scheme, domain, interpolate, reverse }: {
    range: any;
    quantiles?: number | undefined;
    n?: any;
    scheme?: string | undefined;
    domain?: any[] | undefined;
    interpolate: any;
    reverse: any;
}): {
    type: string;
    scale: import("d3-scale").ScaleThreshold<string | number | Date, any, any>;
    domain: any;
    range: any;
};
export function ScaleQuantize(key: any, channels: any, { range, n, scheme, domain, interpolate, reverse }: {
    range: any;
    n?: number | undefined;
    scheme?: string | undefined;
    domain?: (string | number | undefined)[] | undefined;
    interpolate: any;
    reverse: any;
}): {
    type: string;
    scale: import("d3-scale").ScaleThreshold<string | number | Date, any, any>;
    domain: any;
    range: any;
};
export function ScaleThreshold(key: any, channels: any, { domain, unknown, scheme, interpolate, range, reverse }: {
    domain?: number[] | undefined;
    unknown: any;
    scheme?: string | undefined;
    interpolate: any;
    range?: any;
    reverse: any;
}): {
    type: string;
    scale: import("d3-scale").ScaleThreshold<string | number | Date, any, any>;
    domain: any;
    range: any;
};
export function ScaleIdentity(): {
    type: string;
    scale: import("d3-scale").ScaleIdentity<never>;
};
export function inferDomain(channels: any, f?: typeof finite): number[] | (string | undefined)[];
export function interpolatePiecewise(interpolate: any): (i: any, j: any) => (t: any) => any;
export function flip(i: any): (t: any) => any;
import { interpolateNumber } from "d3-interpolate";
import { finite } from "../defined.js";
