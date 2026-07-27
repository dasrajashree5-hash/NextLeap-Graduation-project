import { describe, expect, it } from "vitest";
import { ApiError } from "./api";

describe("ApiError", () => {
  it("exposes status and name", () => {
    const err = new ApiError("Not found", 404, { error: { message: "Not found" } });
    expect(err.name).toBe("ApiError");
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not found");
  });
});

describe("getApiBase", () => {
  it("defaults to local backend when env unset", async () => {
    const prev = process.env.NEXT_PUBLIC_API_URL;
    delete process.env.NEXT_PUBLIC_API_URL;
    const { getApiBase } = await import("./api");
    expect(getApiBase()).toBe("http://127.0.0.1:8000");
    process.env.NEXT_PUBLIC_API_URL = prev;
  });
});
