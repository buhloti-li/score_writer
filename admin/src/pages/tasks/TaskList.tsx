import { useState } from "react";
import { Table, Tabs, Tag, Button, Space, message } from "antd";
import { EyeOutlined, CheckOutlined, DeleteOutlined } from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { taskApi } from "../../lib/api";
import dayjs from "dayjs";

const STATUS_COLORS: Record<string, string> = {
  pending: "default",
  processing: "processing",
  review: "warning",
  approved: "success",
  rejected: "error",
  delivered: "cyan",
  discarded: "default",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "待处理",
  processing: "处理中",
  review: "待审核",
  approved: "已通过",
  rejected: "已拒绝",
  delivered: "已交付",
  discarded: "已丢弃",
};

const PRIORITY_COLORS: Record<string, string> = {
  normal: "default",
  high: "orange",
  urgent: "red",
};

const PRIORITY_LABELS: Record<string, string> = {
  normal: "普通",
  high: "高",
  urgent: "紧急",
};

export default function TaskList() {
  const [activeTab, setActiveTab] = useState("customer_transcribe");
  const [page, setPage] = useState(1);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();

  const taskType = activeTab === "all" ? undefined : activeTab;

  const { data, isLoading } = useQuery({
    queryKey: ["tasks", taskType, page],
    queryFn: () =>
      taskApi.list({
        task_type: taskType,
        page,
        page_size: 20,
      }),
  });

  const approveMut = useMutation({
    mutationFn: (id: string) => taskApi.approve(id),
    onSuccess: () => {
      messageApi.success("已通过");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const discardMut = useMutation({
    mutationFn: (id: string) => taskApi.discard(id),
    onSuccess: () => {
      messageApi.success("已丢弃");
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const columns = [
    {
      title: "曲名",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
    },
    {
      title: "类型",
      dataIndex: "type",
      key: "type",
      width: 120,
      render: (type: string) => {
        const labels: Record<string, string> = {
          customer_transcribe: "客户打谱",
          proactive_import: "主动入库",
          proactive_transcribe: "主动打谱",
        };
        return labels[type] || type;
      },
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (status: string) => (
        <Tag color={STATUS_COLORS[status]}>{STATUS_LABELS[status] || status}</Tag>
      ),
    },
    {
      title: "优先级",
      dataIndex: "priority",
      key: "priority",
      width: 80,
      render: (priority: string) => (
        <Tag color={PRIORITY_COLORS[priority]}>
          {PRIORITY_LABELS[priority] || priority}
        </Tag>
      ),
    },
    {
      title: "截止时间",
      dataIndex: "deadline_at",
      key: "deadline_at",
      width: 160,
      render: (val: string | null) => {
        if (!val) return "-";
        const deadline = dayjs(val);
        const isOverdue = deadline.isBefore(dayjs());
        return (
          <span style={{ color: isOverdue ? "#cf1322" : undefined }}>
            {deadline.format("YYYY-MM-DD HH:mm")}
          </span>
        );
      },
    },
    {
      title: "创建时间",
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
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/tasks/${record.id}`)}
          >
            详情
          </Button>
          {record.status === "review" && (
            <Button
              type="link"
              icon={<CheckOutlined />}
              onClick={() => approveMut.mutate(record.id)}
              loading={approveMut.isPending}
            >
              通过
            </Button>
          )}
          {!["delivered", "discarded", "approved"].includes(record.status) && (
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={() => discardMut.mutate(record.id)}
              loading={discardMut.isPending}
            >
              丢弃
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const tabItems = [
    { key: "customer_transcribe", label: `客户任务 (${activeTab === "customer_transcribe" ? data?.total || 0 : "..."})` },
    { key: "proactive_import", label: "主动入库" },
    { key: "proactive_transcribe", label: "主动打谱" },
    { key: "all", label: "全部" },
  ];

  return (
    <div>
      {contextHolder}
      <h2 style={{ marginBottom: 16 }}>任务中心</h2>

      <Tabs
        activeKey={activeTab}
        onChange={(key) => {
          setActiveTab(key);
          setPage(1);
        }}
        items={tabItems}
      />

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
        rowClassName={(record) => {
          if (
            record.type === "customer_transcribe" &&
            record.deadline_at &&
            dayjs(record.deadline_at).isBefore(dayjs())
          ) {
            return "urgent-row";
          }
          return "";
        }}
      />
    </div>
  );
}
