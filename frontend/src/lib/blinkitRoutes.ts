import type { MobileTab } from "@/components/blinkit/BottomNav";

export function tabFromPath(pathname: string): MobileTab {
  if (pathname.startsWith("/discover")) return "discover";
  if (pathname.startsWith("/categories")) return "categories";
  if (pathname.startsWith("/cart")) return "cart";
  return "home";
}

export function pathForTab(tab: MobileTab): string {
  switch (tab) {
    case "discover":
      return "/discover";
    case "categories":
      return "/categories";
    case "cart":
      return "/cart";
    default:
      return "/";
  }
}
