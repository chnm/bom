export function Context({ document }?: {
    document?: Document | undefined;
}): {
    document: Document;
};
export function create(name: any, { document }: {
    document: any;
}): import("d3-selection").Selection<any, any, null, undefined>;
