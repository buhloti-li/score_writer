import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Select,
  Input,
  message,
  Divider,
  Image,
  Row,
  Col,
} from "antd";
import { taskApi } from "../../lib/api";
import dayjs from "dayjs";
import { useState } from "react";

const STATUS_LABELS: Record<string, string> = {
  pending: "待处理",
  processing: "处理中",
  review: "待审核",
  approved: "已通过",
  rejected: "已拒绝",
  delivered: "已交付",
  discarded: "已丢弃",
};

export default function TaskDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [messageApi, contextHolder] = message.useMessage();
  const [notes, setNotes] = useState("");
  const [newStatus, setNewStatus] = useState<string | undefined>();

  const { data: task, isLoading } = useQuery({
    queryKey: ["task", id],
    queryFn: () => taskApi.get(id!),
    enabled: !!id,
  });

  const updateMut = useMutation({
    mutationFn: (data: any) => taskApi.update(id!, data),
    onSuccess: () => {
      messageApi.success("更新成功");
      queryClient.invalidateQueries({ queryKey: ["task", id] });
    },
    onError: (err: any) => {
      messageApi.error(err.response?.data?.detail || "更新失败");
    },
  });

  const approveMut = useMutation({
    mutationFn: () => taskApi.approve(id!, { admin_notes: notes }),
    onSuccess: () => {
      messageApi.success("审核通过");
      queryClient.invalidateQueries({ queryKey: ["task", id] });
    },
    onError: (err: any) => {
      messageApi.error(err.response?.data?.detail || "操作失败");
    },
  });

  const discardMut = useMutation({
    mutationFn: () => taskApi.discard(id!),
    onSuccess: () => {
      messageApi.success("已丢弃");
      navigate("/tasks");
    },
  });

  if (isLoading) return <Card loading />;
  if (!task) return <Card>任务不存在</Card>;

  const typeLabels: Record<string, string> = {
    customer_transcribe: "客户打谱",
    proactive_import: "主动入库",
    proactive_transcribe: "主动打谱",
  };

  return (
    <div>
      {contextHolder}
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <h2>任务详情</h2>
        <Button onClick={() => navigate("/tasks")}>返回列表</Button>
      </div>

      <Card>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="曲名" span={2}>{task.title}</Descriptions.Item>
          <Descriptions.Item label="类型">{typeLabels[task.type] || task.type}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag>{STATUS_LABELS[task.status] || task.status}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="优先级">
            <Tag color={task.priority === "urgent" ? "red" : task.priority === "high" ? "orange" : "default"}>
              {task.priority}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="来源">{task.source || "-"}</Descriptions.Item>
          <Descriptions.Item label="截止时间">
            {task.deadline_at ? dayjs(task.deadline_at).format("YYYY-MM-DD HH:mm") : "无"}
          </Descriptions.Item>
          <Descriptions.Item label="AI 置信度">
            {task.confidence_score != null ? `${(task.confidence_score * 100).toFixed(1)}%` : "-"}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {dayjs(task.created_at).format("YYYY-MM-DD HH:mm:ss")}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {dayjs(task.updated_at).format("YYYY-MM-DD HH:mm:ss")}
          </Descriptions.Item>
          {task.output_pdf_url && (
            <Descriptions.Item label="输出 PDF" span={2}>
              <a href={task.output_pdf_url} target="_blank" rel="noreferrer">
                查看 PDF
              </a>
            </Descriptions.Item>
          )}
          {task.admin_notes && (
            <Descriptions.Item label="管理员备注" span={2}>
              {task.admin_notes}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      {/* Review Editor: side-by-side original image + score */}
      {task.type !== "proactive_import" && (
        <Card title="审核编辑器" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <h4>原始图片</h4>
              <div style={{ border: "1px solid #d9d9d9", borderRadius: 8, padding: 16, minHeight: 400, background: "#fafafa", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {task.original_images?.length > 0 ? (
                  <Image.PreviewGroup>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                      {task.original_images.map((url: string, i: number) => (
                        <Image key={i} src={url} width={200} />
                      ))}
                    </div>
                  </Image.PreviewGroup>
                ) : (
                  <span style={{ color: "#999" }}>无原始图片</span>
                )}
              </div>
            </Col>
            <Col span={12}>
              <h4>乐谱预览</h4>
              <div style={{ border: "1px solid #d9d9d9", borderRadius: 8, padding: 16, minHeight: 400, background: "#fafafa", display: "flex", alignItems: "center", justifyContent: "center" }}>
                {task.output_pdf_url ? (
                  <iframe src={task.output_pdf_url} style={{ width: "100%", height: 400, border: "none" }} title="Score preview" />
                ) : (
                  <span style={{ color: "#999" }}>等待 AI 打谱结果...</span>
                )}
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* Actions */}
      {!["delivered", "discarded"].includes(task.status) && (
        <Card title="操作" style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: "100%" }}>
            <div>
              <label>管理员备注：</label>
              <Input.TextArea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="可选，添加审核备注"
                rows={3}
                style={{ marginTop: 8 }}
              />
            </div>

            <div>
              <label>更新状态：</label>
              <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                <Select
                  value={newStatus}
                  onChange={setNewStatus}
                  placeholder="选择新状态"
                  style={{ width: 200 }}
                  options={[
                    { value: "pending", label: "待处理" },
                    { value: "processing", label: "处理中" },
                    { value: "review", label: "待审核" },
                  ]}
                />
                <Button
                  onClick={() => {
                    if (newStatus) {
                      updateMut.mutate({ status: newStatus, admin_notes: notes || undefined });
                    }
                  }}
                  disabled={!newStatus}
                >
                  更新状态
                </Button>
              </div>
            </div>

            <Divider />

            <Space>
              {task.status === "review" && (
                <Button type="primary" onClick={() => approveMut.mutate()} loading={approveMut.isPending}>
                  审核通过
                </Button>
              )}
              <Button danger onClick={() => discardMut.mutate()} loading={discardMut.isPending}>
                丢弃任务
              </Button>
            </Space>
          </Space>
        </Card>
      )}
    </div>
  );
}
