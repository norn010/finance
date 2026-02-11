import { Alert, Button, Card, Descriptions, Space, Typography } from "antd";
import { ResultTable } from "../components/ResultTable";
import type { PreviewPayload, TransformOptions } from "../services/api";
import { downloadTransform } from "../services/api";

interface PreviewPageProps {
  file: File;
  options: TransformOptions;
  preview: PreviewPayload;
  onBack: () => void;
}

function saveBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export function PreviewPage({ file, options, preview, onBack }: PreviewPageProps) {
  async function handleDownload() {
    const blob = await downloadTransform(file, options);
    saveBlob(blob, "finance-screening-output.xlsx");
  }

  return (
    <Card title="Preview และ Export">
      {preview.issues.length > 0 && (
        <Alert
          type="warning"
          message="พบประเด็นที่ควรตรวจสอบ"
          description={preview.issues.join(" | ")}
          style={{ marginBottom: 16 }}
        />
      )}
      <Descriptions bordered size="small" column={3} style={{ marginBottom: 16 }}>
        <Descriptions.Item label="Rows In">{preview.stats.rows_in}</Descriptions.Item>
        <Descriptions.Item label="Rows Out">{preview.stats.rows_out}</Descriptions.Item>
        <Descriptions.Item label="Duplicate Groups">{preview.stats.duplicate_tank_groups}</Descriptions.Item>
        <Descriptions.Item label="Duplicate Rows">{preview.stats.duplicate_rows}</Descriptions.Item>
        <Descriptions.Item label="Finance Sent">{preview.stats.finance_sent_count}</Descriptions.Item>
        <Descriptions.Item label="Finance Broker">{preview.stats.finance_broker_count}</Descriptions.Item>
      </Descriptions>

      <Typography.Paragraph>ตัวอย่างข้อมูลสูงสุด 200 แถวแรก</Typography.Paragraph>
      <ResultTable columns={preview.columns} rows={preview.rows} />

      <Space style={{ marginTop: 16 }}>
        <Button onClick={onBack}>กลับไปแก้ Mapping</Button>
        <Button type="primary" onClick={handleDownload}>
          ดาวน์โหลดไฟล์ผลลัพธ์
        </Button>
      </Space>
    </Card>
  );
}
