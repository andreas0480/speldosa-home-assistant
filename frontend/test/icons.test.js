import { expect, it } from "vitest";

it("registers the Speldosa mark as the icon set 'speldosa'", async () => {
  const { SPELDOSA_ICONS } = await import("../../custom_components/speldosa/frontend/speldosa-icons.js");
  const set = window.customIcons.speldosa;
  expect(set).toBeDefined();
  const icon = await set.getIcon("logo");
  expect(icon).toBe(SPELDOSA_ICONS.logo);
  expect(icon.viewBox).toBe("-46 -46 92 92");
  // Ring (two circles), play triangle, two waves: five closed shapes.
  expect(icon.path.match(/Z/g)).toHaveLength(5);
  expect(await set.getIconList()).toEqual([{ name: "logo" }]);
});
