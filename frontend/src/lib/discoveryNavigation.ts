/** URL for the Discover tab with an optional prompt (works as a real href before React hydrates). */
export function discoverHref(prompt?: string): string {
  const trimmed = prompt?.trim();
  if (!trimmed) return "/discover";
  return `/discover?prompt=${encodeURIComponent(trimmed)}`;
}
