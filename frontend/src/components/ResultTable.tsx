import { Table } from "antd";

interface ResultTableProps {
  columns: string[];
  rows: Record<string, unknown>[];
}

export function ResultTable({ columns, rows }: ResultTableProps) {
  const tableColumns = columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true
  }));

  return (
    <Table
      rowKey={(_, index) => `${index ?? 0}`}
      columns={tableColumns}
      dataSource={rows}
      bordered
      pagination={{ pageSize: 20 }}
      scroll={{ x: "max-content" }}
      size="small"
    />
  );
}
