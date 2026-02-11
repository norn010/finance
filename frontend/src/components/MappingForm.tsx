import { Button, Form, Input, Select, Space } from "antd";
import type { TransformOptions } from "../services/api";

interface MappingFormProps {
  initialValues: TransformOptions;
  onSubmit: (values: TransformOptions) => void;
  submitting?: boolean;
}

export function MappingForm({ initialValues, onSubmit, submitting }: MappingFormProps) {
  return (
    <Form
      layout="vertical"
      initialValues={initialValues}
      onFinish={(values) => onSubmit(values as TransformOptions)}
    >
      <Space wrap>
        <Form.Item name={["mapping", "tank_no"]} label="คอลัมน์เลขถัง">
          <Input />
        </Form.Item>
        <Form.Item name={["mapping", "item"]} label="คอลัมน์รายการ">
          <Input />
        </Form.Item>
        <Form.Item name={["mapping", "sale_price"]} label="คอลัมน์ราคาขาย">
          <Input />
        </Form.Item>
        <Form.Item name={["mapping", "total_value"]} label="คอลัมน์มูลค่ารวม">
          <Input />
        </Form.Item>
      </Space>

      <Space wrap>
        <Form.Item name={["mapping", "product_value"]} label="คอลัมน์มูลค่าสินค้า">
          <Input />
        </Form.Item>
        <Form.Item name={["mapping", "tax"]} label="คอลัมน์ภาษี">
          <Input />
        </Form.Item>
        <Form.Item name={["mapping", "com_fn"]} label="คอลัมน์ COM F/N">
          <Input />
        </Form.Item>
        <Form.Item name={["mapping", "com"]} label="คอลัมน์ COM">
          <Input />
        </Form.Item>
      </Space>

      <Space wrap>
        <Form.Item name="finance_sent_item_label" label="รายการสำหรับส่งไฟแนนซ์">
          <Input />
        </Form.Item>
        <Form.Item name="finance_broker_item_label" label="รายการสำหรับนายหน้าไฟแนนซ์">
          <Input />
        </Form.Item>
        <Form.Item name="duplicate_mode" label="โหมดเลขถังซ้ำ">
          <Select
            options={[
              { value: "group", label: "group - ยุบเลขถังซ้ำ" },
              { value: "keep", label: "keep - คงทุกรายการ" }
            ]}
          />
        </Form.Item>
      </Space>

      <Button type="primary" htmlType="submit" loading={submitting}>
        Preview
      </Button>
    </Form>
  );
}
