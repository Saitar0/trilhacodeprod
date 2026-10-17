import { render, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IconCatalog } from "./IconCatalog";

describe("IconCatalog", () => {
  it("renders an icon used by the content catalog", async () => {
    render(<IconCatalog name="BookOpen" className="test-icon" />);

    await waitFor(() => {
      expect(document.querySelector("svg")).toHaveClass("test-icon");
      expect(document.querySelector("svg")).toHaveAttribute("data-icon", "BookOpen");
    });
  });

  it("renders valid Lucide icons beyond the previously bundled subset", async () => {
    const { container } = render(<IconCatalog name="ZoomIn" />);

    await waitFor(() => {
      expect(container.querySelector("svg")).toHaveAttribute("data-icon", "ZoomIn");
    });
  });

  it("falls back to Square for unknown or missing names", () => {
    const { container, rerender } = render(<IconCatalog name="UnknownIcon" />);
    expect(container.querySelector("svg")).toHaveAttribute("data-icon", "Square");

    rerender(<IconCatalog />);
    expect(container.querySelector("svg")).toHaveAttribute("data-icon", "Square");
  });
});
