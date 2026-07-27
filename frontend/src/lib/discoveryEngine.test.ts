import { describe, expect, it } from "vitest";
import { discoverFromPrompt } from "./discoveryEngine";

describe("discoverFromPrompt", () => {
  it("returns pasta-themed groups for pasta prompts", () => {
    const groups = discoverFromPrompt("I'm making pasta tonight");
    expect(groups.length).toBeGreaterThan(0);
    expect(groups.some((g) => g.title.includes("Main Ingredients"))).toBe(true);
  });

  it("returns default groups for empty prompt", () => {
    const groups = discoverFromPrompt("");
    expect(groups.length).toBeGreaterThan(0);
  });
});
