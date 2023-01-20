export function ScaleOrdinal(key: any, channels: any, { type, interval, domain, range, scheme, unknown, ...options }: {
    [x: string]: any;
    type: any;
    interval: any;
    domain: any;
    range: any;
    scheme: any;
    unknown: any;
}): {
    type: any;
    domain: any;
    range: any;
    scale: any;
    hint: any;
    interval: any;
};
export function ScalePoint(key: any, channels: any, { align, padding, ...options }: {
    [x: string]: any;
    align?: number | undefined;
    padding?: number | undefined;
}): any;
export function ScaleBand(key: any, channels: any, { align, padding, paddingInner, paddingOuter, ...options }: {
    [x: string]: any;
    align?: number | undefined;
    padding?: number | undefined;
    paddingInner?: any;
    paddingOuter?: any;
}): any;
export const ordinalImplicit: unique symbol;
