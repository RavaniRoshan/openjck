import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatDuration(ms) {
  if (ms == null) return "—";
  return ms < 1000 ? Math.round(ms) + "ms" : (ms / 1000).toFixed(2) + "s";
}

export function formatRelative(iso) {
  if (!iso) return "unknown";
  const diff = Math.round((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return diff + "s ago";
  if (diff < 3600) return Math.round(diff / 60) + "m ago";
  if (diff < 86400) return Math.round(diff / 3600) + "h ago";
  return Math.round(diff / 86400) + "d ago";
}

export function formatStamp(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function statusClass(status) {
  return ["completed", "failed", "running"].includes(status) ? status : "unknown";
}

export function formatCurrency(num) {
  if (num == null) return "—";
  const val = Number(num);
  return val > 0 ? "$" + val.toFixed(4) : "—";
}
