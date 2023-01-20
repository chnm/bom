import type { Primitive } from "d3";
export declare function defined(x: Primitive | undefined): boolean;
export declare function ascendingDefined(a: Primitive | undefined, b: Primitive | undefined): number;
export declare function descendingDefined(a: Primitive | undefined, b: Primitive | undefined): number;
export declare function nonempty(x: unknown): boolean;
export declare function finite(x: number): number;
export declare function positive(x: number): number;
export declare function negative(x: number): number;
