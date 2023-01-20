export function Channel(data: any, { scale, type, value, filter, hint }: {
    scale: any;
    type: any;
    value: any;
    filter: any;
    hint: any;
}): {
    scale: any;
    type: any;
    value: any;
    label: any;
    filter: any;
    hint: any;
};
export function Channels(descriptors: any, data: any): {
    [k: string]: {
        scale: any;
        type: any;
        value: any;
        label: any;
        filter: any;
        hint: any;
    };
};
export function valueObject(channels: any, scales: any): {
    [k: string]: any;
};
export function channelDomain(channels: any, facetChannels: any, data: any, options: any): void;
