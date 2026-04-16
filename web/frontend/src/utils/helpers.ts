/**
 * Small utility functions used across the app.
 */

/**
 * Format a grid system ID like "ieee118" → "IEEE 118"
 */
export function formatGrid(grid: string): string {
  return grid.replace(/^ieee/, "IEEE ");
}

/**
 * Clamp a number between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Debounce: returns a function that delays calling fn until after wait ms.
 */
export function debounce<T extends (...args: unknown[]) => unknown>(fn: T, wait: number): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

/**
 * Format a Date or ISO string to "Mar 18, 2026 14:35"
 */
export function formatDateTime(dt: string | Date | null | undefined): string {
  if (!dt) return "—";
  return new Date(dt).toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}
