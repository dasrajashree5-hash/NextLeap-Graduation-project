import { describe, expect, it } from "vitest";
import { discoverHref } from "./discoveryNavigation";

describe("discoverHref", () => {
  it("returns /discover when prompt is empty", () => {
    expect(discoverHref()).toBe("/discover");
    expect(discoverHref("  ")).toBe("/discover");
  });

  it("encodes prompt in query string", () => {
    expect(discoverHref("I'm making pasta tonight.")).toBe(
      "/discover?prompt=I'm%20making%20pasta%20tonight."
    );
  });
});
