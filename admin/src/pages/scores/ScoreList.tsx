import { useState } from "react";
import { Table, Button, Space, Tag, Popconfirm, message, Input } from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { scoreApi } from "../../lib/api";
import dayjs from "dayjs";

const STATUS_MAP: Record<string, { label: string; color: string }> = {
  available: { label: "在售", color: "green" },
  producing: { label: "制作中", color: "orange" },
  offline: { label: "已下架", color: "default" },
};

export default function ScoreList() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();

  const { data, isLoading } = useQuery({
    queryKey: ["admin-scores", page],
    queryFn: () => scoreApi.list({ page, page_size: 20 }),
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => scoreApi.delete(id),
    onSuccess: () => {
      messageApi.success("已删除");
      queryClient.invalidateQueries({ queryKey: ["admin-scores"] });
    },
    onError: () => messageApi.error("删除失败"),
  });

  const columns = [
    {
      title: "曲名",
      dataIndex: "title",
      key: "title",
      ellipsis: true,
      render: (title: string, record: any) => (
        <div>
          <div>{title}</div>
          {record.title_en && <div style={{ fontSize: 12, color: "#999" }}>{record.title_en}</div>}
        </div>
      ),
    },
    { title: "作曲", dataIndex: "composer", key: "composer", width: 120, ellipsis: true },
    { title: "乐器", dataIndex: "instrument", key: "instrument", width: 100 },
    {
      title: "价格",
      dataIndex: "price",
      key: "price",
      width: 80,
      render: (price: string) => `¥${price}`,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 80,
      render: (status: string) => {
        const s = STATUS_MAP[status] || { label: status, color: "default" };
        return <Tag color={s.color}>{s.label}</Tag>;
      },
    },
    {
      title: "下载量",
      dataIndex: "download_count",
      key: "download_count",
      width: 80,
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      width: 120,
      render: (val: string) => dayjs(val).format("YYYY-MM-DD"),
    },
    {
      title: "操作",
      key: "action",
      width: 160,
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => navigate(`/scores/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此乐谱？"
            onConfirm={() => deleteMut.mutate(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {contextHolder}
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <h2>乐谱管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/scores/new")}>
          添加乐谱
        </Button>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索乐谱..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 300 }}
        />
      </div>

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
