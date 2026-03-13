import { Layout, Menu } from "antd";
import {
  DashboardOutlined,
  FileTextOutlined,
  OrderedListOutlined,
  ShoppingCartOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../lib/auth";

const { Header, Sider, Content } = Layout;

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const menuItems = [
    { key: "/", icon: <DashboardOutlined />, label: "仪表盘" },
    { key: "/tasks", icon: <OrderedListOutlined />, label: "任务中心" },
    { key: "/scores", icon: <FileTextOutlined />, label: "乐谱管理" },
    { key: "/orders", icon: <ShoppingCartOutlined />, label: "订单管理" },
  ];

  const selectedKey = menuItems.find(
    (item) => item.key !== "/" && location.pathname.startsWith(item.key)
  )?.key || "/";

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider breakpoint="lg" collapsedWidth="80">
        <div className="logo">
          <FileTextOutlined /> 乐谱管理
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            borderBottom: "1px solid #f0f0f0",
          }}
        >
          <span style={{ marginRight: 16 }}>
            {user?.nickname || user?.email || "管理员"}
          </span>
          <LogoutOutlined
            onClick={() => {
              logout();
              navigate("/login");
            }}
            style={{ cursor: "pointer", fontSize: 16 }}
          />
        </Header>
        <Content style={{ margin: "24px 16px", padding: 24, background: "#fff", borderRadius: 8 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
