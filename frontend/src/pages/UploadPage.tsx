import { Alert, Button, Card, Typography, Upload } from "antd";
import type { UploadProps } from "antd";
import { useState } from "react";
import { MappingForm } from "../components/MappingForm";
import type { PreviewPayload, TransformOptions } from "../services/api";
import { previewTransform } from "../services/api";

const defaultOptions: TransformOptions = {
  mapping: {
    tank_no: "เลขตัวถัง",
    item: "รายการ",
    sale_price: "มูลค่ารวม",
    total_value: "มูลค่ารวม",
    product_value: "มูลค่าสินค้า",
    tax: "ภาษี",
    com_fn: "มูลค่าสินค้า",
    com: "ภาษี"
  },
  duplicate_mode: "keep",
  finance_sent_item_label: "ส่งไฟแนนซ์",
  finance_broker_item_label: "นายหน้าไฟแนนซ์"
};

interface UploadPageProps {
  onPreviewReady: (payload: {
    file: File;
    options: TransformOptions;
    preview: PreviewPayload;
  }) => void;
}

export function UploadPage({ onPreviewReady }: UploadPageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadProps: UploadProps = {
    maxCount: 1,
    beforeUpload: (selected) => {
      setFile(selected as File);
      setError(null);
      return false;
    },
    accept: ".xls,.xlsx"
  };

  async function handlePreview(options: TransformOptions) {
    if (!file) {
      setError("กรุณาเลือกไฟล์ Excel ก่อน");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const preview = await previewTransform(file, options);
      onPreviewReady({ file, options, preview });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="Upload และตั้งค่า Mapping">
      <Typography.Paragraph>
        อัปโหลดไฟล์ภาษีขาย แล้วกด Preview เพื่อตรวจสอบผลคัดกรองก่อนดาวน์โหลดไฟล์ใหม่
      </Typography.Paragraph>

      <Upload {...uploadProps}>
        <Button>เลือกไฟล์ Excel</Button>
      </Upload>
      {file && <Typography.Text>ไฟล์ที่เลือก: {file.name}</Typography.Text>}
      {error && <Alert style={{ marginTop: 12 }} type="error" message={error} />}

      <div style={{ marginTop: 16 }}>
        <MappingForm initialValues={defaultOptions} onSubmit={handlePreview} submitting={loading} />
      </div>
    </Card>
  );
}
