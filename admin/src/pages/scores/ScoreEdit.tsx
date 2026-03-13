import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, Form, Input, InputNumber, Select, Button, message, Row, Col } from "antd";
import { scoreApi } from "../../lib/api";
import { useEffect } from "react";

const INSTRUMENTS = ["钢琴", "吉他", "小提琴", "大提琴", "长笛", "声乐", "萨克斯", "单簧管", "其他"];
const GENRES = ["古典", "流行", "爵士", "宗教", "民族", "影视", "儿童", "其他"];

export default function ScoreEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [messageApi, contextHolder] = message.useMessage();
  const isEdit = !!id;

  const { data: score, isLoading } = useQuery({
    queryKey: ["score", id],
    queryFn: () => scoreApi.get(id!),
    enabled: isEdit,
  });

  useEffect(() => {
    if (score) {
      form.setFieldsValue({
        ...score,
        tags: score.tags?.join(", ") || "",
      });
    }
  }, [score, form]);

  const saveMut = useMutation({
    mutationFn: async (values: any) => {
      const data = {
        ...values,
        tags: values.tags
          ? values.tags.split(",").map((t: string) => t.trim()).filter(Boolean)
          : [],
        price: String(values.price || 0),
      };
      if (isEdit) {
        return scoreApi.update(id!, data);
      }
      return scoreApi.create(data);
    },
    onSuccess: () => {
      messageApi.success(isEdit ? "更新成功" : "创建成功");
      queryClient.invalidateQueries({ queryKey: ["admin-scores"] });
      navigate("/scores");
    },
    onError: (err: any) => {
      messageApi.error(err.response?.data?.detail || "保存失败");
    },
  });

  return (
    <div>
      {contextHolder}
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
        <h2>{isEdit ? "编辑乐谱" : "添加乐谱"}</h2>
        <Button onClick={() => navigate("/scores")}>返回列表</Button>
      </div>

      <Card loading={isEdit && isLoading}>
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => saveMut.mutate(values)}
          initialValues={{
            price: 0,
            difficulty: 3,
            copyright_status: "unknown",
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="title"
                label="曲名（中文）"
                rules={[{ required: true, message: "请输入曲名" }]}
              >
                <Input placeholder="如：月光奏鸣曲" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="title_en" label="曲名（英文）">
                <Input placeholder="如：Moonlight Sonata" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="composer" label="作曲家">
                <Input placeholder="如：贝多芬" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="arranger" label="编曲者">
                <Input />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="lyricist" label="作词者">
                <Input />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="instrument" label="乐器">
                <Select placeholder="选择乐器" allowClear>
                  {INSTRUMENTS.map((i) => (
                    <Select.Option key={i} value={i}>{i}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="genre" label="风格">
                <Select placeholder="选择风格" allowClear>
                  {GENRES.map((g) => (
                    <Select.Option key={g} value={g}>{g}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="key_signature" label="调号">
                <Input placeholder="C大调" />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="time_signature" label="拍号">
                <Input placeholder="4/4" />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item name="difficulty" label="难度 (1-5)">
                <InputNumber min={1} max={5} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={6}>
              <Form.Item name="price" label="价格 (¥)">
                <InputNumber min={0} precision={2} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="page_count" label="页数">
                <InputNumber min={1} style={{ width: "100%" }} />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="copyright_status" label="版权状态">
                <Select>
                  <Select.Option value="public_domain">公共领域</Select.Option>
                  <Select.Option value="licensed">已授权</Select.Option>
                  <Select.Option value="user_only">仅用户</Select.Option>
                  <Select.Option value="unknown">未知</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item name="status" label="状态">
                <Select>
                  <Select.Option value="available">在售</Select.Option>
                  <Select.Option value="producing">制作中</Select.Option>
                  <Select.Option value="offline">已下架</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="tags" label="标签（逗号分隔）">
            <Input placeholder="经典, 初学者, 考级" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <Input.TextArea rows={4} placeholder="乐谱描述信息..." />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={saveMut.isPending}>
              {isEdit ? "保存修改" : "创建乐谱"}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
