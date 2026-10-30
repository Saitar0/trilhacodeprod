import { describe, expect, it } from "vitest";
import { isTypedActivitiesEnabled } from "./typedActivityFeature";

describe("typed activities feature flag", () => {
  it("fica desligada quando ausente ou explicitamente false", () => {
    expect(isTypedActivitiesEnabled(undefined)).toBe(false);
    expect(isTypedActivitiesEnabled("false")).toBe(false);
    expect(isTypedActivitiesEnabled("")).toBe(false);
  });

  it("só liga com o valor explícito true", () => {
    expect(isTypedActivitiesEnabled("true")).toBe(true);
    expect(isTypedActivitiesEnabled("1")).toBe(false);
    expect(isTypedActivitiesEnabled("TRUE")).toBe(false);
  });
});