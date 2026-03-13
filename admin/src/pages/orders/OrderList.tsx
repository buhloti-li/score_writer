import { useState } from "react";
import { Table, Tag, Button, Space, message, Popconfirm } from "antd";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { orderApi } from "../../lib/api";
import dayjs from "dayjs";

const PAYMENT_STATUS: Record<string, { label: string; color: string }> = {
  pending: { label: "待支付", color: "default" },
  paid: { label: "已支付", color: "green" },
  refunded: { label: "已退款", color: "red" },
};

const DELIVERY_STATUS: Record<string, { label: string; color: string }> = {
  pending: { label: "待发货", color: "orange" },
  delivered: { label: "已发货", color: "green" },
};

export default function OrderList() {
  const [page, setPage] = useState(1);
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();

  const { data, isLoading } = useQuery({
    queryKey: ["admin-orders", page],
    queryFn: () => orderApi.list({ page, page_size: 20 }),
  });

  const deliverMut = useMutation({
    mutationFn: (id: string) => orderApi.deliver(id),
    onSuccess: () => {
      messageApi.success("已发货");
      queryClient.invalidateQueries({ queryKey: ["admin-orders"] });
    },
    onError: (err: any) => messageApi.error(err.response?.data?.detail || "操作失败"),
  });

  const refundMut = useMutation({
    mutationFn: (id: string) => orderApi.refund(id),
    onSuccess: () => {
      messageApi.success("已退款");
      queryClient.invalidateQueries({ queryKey: ["admin-orders"] });
    },
    onError: (err: any) => messageApi.error(err.response?.data?.detail || "操作失败"),
  });

  const columns = [
    {
      title: "订单号",
      dataIndex: "id",
      key: "id",
      width: 120,
      ellipsis: true,
      render: (id: string) => id.slice(0, 8) + "...",
    },
    {
      title: "金额",
      dataIndex: "amount",
      key: "amount",
      width: 80,
      render: (amount: string) => `¥${amount}`,
    },
    {
      title: "来源",
      dataIndex: "source",
      key: "source",
      width: 80,
      render: (source: string) => source === "taobao" ? "淘宝" : "网站",
    },
    {
      title: "支付状态",
      dataIndex: "payment_status",
      key: "payment_status",
      width: 100,
      render: (status: string) => {
        const s = PAYMENT_STATUS[status] || { label: status, color: "default" };
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: "发货状态",
      dataIndex: "delivery_status",
      key: "delivery_status",
      width: 100,
      render: (status: string) => {
        const s = DELIVERY_STATUS[status] || { label: status, color: "default" };
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: "下单时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 160,
      render: (val: string) => dayjs(val).format("YYYY-MM-DD HH:mm"),
    },
    {
      title: "操作",
      key: "action",
      width: 200,
      render: (_: any, record: any) => (
        <Space>
          {record.payment_status === "paid" && record.delivery_status === "pending" && (
            <Popconfirm
              title="确定发货？"
              onConfirm={() => deliverMut.mutate(record.id)}
            >
              <Button type="link">发货</Button>
            </Popconfirm>
          )}
          {record.payment_status === "paid" && (
            <Popconfirm
              title="确定退款？"
              onConfirm={() => refundMut.mutate(record.id)}
            >
              <Button type="link" danger>退款</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      {contextHolder}
      <h2 style={{ marginBottom: 16 }}>订单管理</h2>

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          total: data?.total || 0,
          pageSize: 20,
          onChange: setPage,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />
    </div>
  );
}
