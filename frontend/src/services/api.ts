export type DuplicateMode = "keep" | "group";

export interface ColumnMapping {
  tank_no: string;
  item: string;
  sale_price: string;
  total_value: string;
  product_value: string;
  tax: string;
  com_fn: string;
  com: string;
}

export interface TransformOptions {
  mapping: ColumnMapping;
  duplicate_mode: DuplicateMode;
  finance_sent_item_label: string;
  finance_broker_item_label: string;
}

export interface PreviewPayload {
  columns: string[];
  rows: Record<string, unknown>[];
  stats: Record<string, number>;
  issues: string[];
}

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function toFormData(file: File, options: TransformOptions): FormData {
  const form = new FormData();
  form.append("file", file);
  form.append("config", JSON.stringify(options));
  return form;
}

export async function previewTransform(file: File, options: TransformOptions): Promise<PreviewPayload> {
  const response = await fetch(`${API_BASE}/api/preview`, {
    method: "POST",
    body: toFormData(file, options)
  });
  if (!response.ok) {
    throw new Error(`Preview failed: ${response.status}`);
  }
  return response.json();
}

export async function downloadTransform(file: File, options: TransformOptions): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/transform`, {
    method: "POST",
    body: toFormData(file, options)
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Export failed: ${response.status} ${message}`);
  }
  return response.blob();
}
