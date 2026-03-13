import { Card, Col, Row, Statistic, Tag } from "antd";
import {
  FileTextOutlined,
  OrderedListOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../lib/api";

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: dashboardApi.get,
    refetchInterval: 30_000,
  });

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>仪表盘</h2>

      <Row gutter={[16, 16]}>
        <Col xs={12} sm={6}>
          <Card loading={isLoading}>
            <Statistic
              title="乐谱总数"
              value={data?.total_scores || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card loading={isLoading}>
            <Statistic
              title="待处理任务"
              value={data?.pending_tasks || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={data?.pending_tasks > 0 ? { color: "#cf1322" } : {}}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card loading={isLoading}>
            <Statistic
              title="客户任务"
              value={data?.total_customer_tasks || 0}
              prefix={<OrderedListOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card loading={isLoading}>
            <Statistic
              title="主动入库"
              value={data?.total_import_tasks || 0}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }} loading={isLoading}>
        <h3>系统状态</h3>
        <div style={{ marginTop: 16, display: "flex", gap: 16, flexWrap: "wrap" }}>
          <div>
            队列状态：
            <Tag color={data?.is_queue_idle ? "green" : "orange"}>
              {data?.is_queue_idle ? "空闲" : "繁忙"}
            </Tag>
          </div>
          <div>
            主动打谱任务：
            <Tag>{data?.total_transcribe_tasks || 0} 个</Tag>
          </div>
        </div>
      </Card>
    </div>
  );
}
