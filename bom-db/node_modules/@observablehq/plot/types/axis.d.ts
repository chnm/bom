export function maybeAutoTickFormat(tickFormat: any, domain: any): any;
export class AxisX {
    constructor({ name, axis, ticks, tickSize, tickPadding, tickFormat, fontVariant, grid, label, labelAnchor, labelOffset, line, tickRotate, ariaLabel, ariaDescription }?: {
        name?: string | undefined;
        axis: any;
        ticks: any;
        tickSize?: number | undefined;
        tickPadding?: number | undefined;
        tickFormat: any;
        fontVariant: any;
        grid: any;
        label: any;
        labelAnchor: any;
        labelOffset: any;
        line: any;
        tickRotate: any;
        ariaLabel: any;
        ariaDescription: any;
    });
    name: any;
    axis: string;
    ticks: any;
    tickSize: any;
    tickPadding: any;
    tickFormat: any;
    fontVariant: any;
    grid: any;
    label: any;
    labelAnchor: string | undefined;
    labelOffset: any;
    line: any;
    tickRotate: any;
    ariaLabel: any;
    ariaDescription: any;
    render(index: any, { [this.name]: x, fy }: {
        fy: any;
    }, { width, height, marginTop, marginRight, marginBottom, marginLeft, offsetLeft, facetMarginTop, facetMarginBottom, labelMarginLeft, labelMarginRight }: {
        width: any;
        height: any;
        marginTop: any;
        marginRight: any;
        marginBottom: any;
        marginLeft: any;
        offsetLeft?: number | undefined;
        facetMarginTop: any;
        facetMarginBottom: any;
        labelMarginLeft?: number | undefined;
        labelMarginRight?: number | undefined;
    }, context: any): any;
}
export class AxisY {
    constructor({ name, axis, ticks, tickSize, tickPadding, tickFormat, fontVariant, grid, label, labelAnchor, labelOffset, line, tickRotate, ariaLabel, ariaDescription }?: {
        name?: string | undefined;
        axis: any;
        ticks: any;
        tickSize?: number | undefined;
        tickPadding?: number | undefined;
        tickFormat: any;
        fontVariant: any;
        grid: any;
        label: any;
        labelAnchor: any;
        labelOffset: any;
        line: any;
        tickRotate: any;
        ariaLabel: any;
        ariaDescription: any;
    });
    name: any;
    axis: string;
    ticks: any;
    tickSize: any;
    tickPadding: any;
    tickFormat: any;
    fontVariant: any;
    grid: any;
    label: any;
    labelAnchor: string | undefined;
    labelOffset: any;
    line: any;
    tickRotate: any;
    ariaLabel: any;
    ariaDescription: any;
    render(index: any, { [this.name]: y, fx }: {
        fx: any;
    }, { width, height, marginTop, marginRight, marginBottom, marginLeft, offsetTop, facetMarginLeft, facetMarginRight }: {
        width: any;
        height: any;
        marginTop: any;
        marginRight: any;
        marginBottom: any;
        marginLeft: any;
        offsetTop?: number | undefined;
        facetMarginLeft: any;
        facetMarginRight: any;
    }, context: any): any;
}
