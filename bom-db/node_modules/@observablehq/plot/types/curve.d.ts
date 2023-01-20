import type { CurveFactory, CurveBundleFactory, CurveCardinalFactory, CurveCatmullRomFactory } from "d3";
declare type CurveFunction = CurveFactory | CurveBundleFactory | CurveCardinalFactory | CurveCatmullRomFactory;
declare type CurveName = "basis" | "basis-closed" | "basis-open" | "bundle" | "bump-x" | "bump-y" | "cardinal" | "cardinal-closed" | "cardinal-open" | "catmull-rom" | "catmull-rom-closed" | "catmull-rom-open" | "linear" | "linear-closed" | "monotone-x" | "monotone-y" | "natural" | "step" | "step-after" | "step-before";
export declare function Curve(curve?: CurveName | CurveFunction, tension?: number): CurveFunction;
export {};
