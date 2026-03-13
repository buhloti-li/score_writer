import { Button, Card, Form, Input, message } from "antd";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [messageApi, contextHolder] = message.useMessage();

  const onFinish = async (values: { account: string; password: string }) => {
    try {
      const isEmail = values.account.includes("@");
      await login({
        ...(isEmail ? { email: values.account } : { phone: values.account }),
        password: values.password,
      });
      navigate("/");
    } catch (err: any) {
      messageApi.error(err.response?.data?.detail || err.message || "登录失败");
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", background: "#f0f2f5" }}>
      {contextHolder}
      <Card title="乐谱管理后台登录" style={{ width: 400 }}>
        <Form onFinish={onFinish} size="large">
          <Form.Item name="account" rules={[{ required: true, message: "请输入账号" }]}>
            <Input prefix={<UserOutlined />} placeholder="手机号或邮箱" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
