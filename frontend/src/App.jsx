import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const defaultForm = {
  name: "",
  phone: "",
  gender: "male",
};

const genderOptions = [
  { value: "male", label: "男" },
  { value: "female", label: "女" },
];

export default function App() {
  const [form, setForm] = useState(defaultForm);
  const [customers, setCustomers] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, page_size: 10, total: 0, total_pages: 0 });
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [viewing, setViewing] = useState(null);

  const hasCustomers = useMemo(() => customers && customers.length > 0, [customers]);

  const fetchCustomers = async (page = pagination.page) => {
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/customers`, {
        params: { page, page_size: pagination.page_size },
      });
      setCustomers(res.data.data || []);
      setPagination(res.data.pagination || { page: 1, page_size: 10, total: 0, total_pages: 0 });
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.errors?.join("，") || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleInput = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const resetForm = () => {
    setForm(defaultForm);
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      if (editingId) {
        const res = await axios.put(`${API_BASE}/api/customers/${editingId}`, form);
        setViewing(res.data);
      } else {
        const res = await axios.post(`${API_BASE}/api/customers`, form);
        setViewing(res.data);
      }
      resetForm();
      fetchCustomers(pagination.page);
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.errors?.join("，") || err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (customer) => {
    setEditingId(customer.id);
    setForm({ name: customer.name, phone: customer.phone, gender: customer.gender });
    setViewing(customer);
  };

  const handleView = async (customerId) => {
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/api/customers/${customerId}`);
      setViewing(res.data);
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const handleDelete = async (customerId) => {
    if (!window.confirm("确定删除该客户记录吗？")) return;
    setError("");
    try {
      await axios.delete(`${API_BASE}/api/customers/${customerId}`);
      if (viewing?.id === customerId) {
        setViewing(null);
      }
      if (editingId === customerId) {
        resetForm();
      }
      fetchCustomers(Math.max(1, pagination.page));
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    }
  };

  const changePage = (nextPage) => {
    const target = Math.min(Math.max(nextPage, 1), pagination.total_pages || 1);
    setPagination((prev) => ({ ...prev, page: target }));
    fetchCustomers(target);
  };

  const formatDate = (value) => (value ? new Date(value).toLocaleString() : "-");

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">CUSTOMER MANAGEMENT DEMO</p>
          <h1>客户档案资料系统</h1>
          <p className="subtitle">添加 / 修改 / 查看 / 列表 + 分页，一站式管理客户资料。</p>
        </div>
        <div className="pill">API: {API_BASE}</div>
      </header>

      <section className="grid">
        <div className="card">
          <div className="card-header">
            <div>
              <p className="eyebrow">{editingId ? "编辑客户" : "新增客户"}</p>
              <h2>{editingId ? "更新客户资料" : "创建客户资料"}</h2>
            </div>
            {editingId && (
              <button className="ghost-btn" onClick={resetForm}>
                取消编辑
              </button>
            )}
          </div>
          <form className="form" onSubmit={handleSubmit}>
            <label>
              姓名
              <input name="name" value={form.name} onChange={handleInput} placeholder="请输入客户姓名" required />
            </label>
            <label>
              联系电话
              <input name="phone" value={form.phone} onChange={handleInput} placeholder="手机或座机号" required />
            </label>
            <label>
              性别
              <div className="radio-group">
                {genderOptions.map((option) => (
                  <label key={option.value} className="radio">
                    <input
                      type="radio"
                      name="gender"
                      value={option.value}
                      checked={form.gender === option.value}
                      onChange={handleInput}
                    />
                    <span>{option.label}</span>
                  </label>
                ))}
              </div>
            </label>

            {error && <div className="error">{error}</div>}

            <div className="form-actions">
              <button type="submit" className="primary-btn" disabled={submitting}>
                {submitting ? "提交中..." : editingId ? "保存更新" : "添加客户"}
              </button>
              <button type="button" className="ghost-btn" onClick={resetForm} disabled={submitting}>
                重置
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <p className="eyebrow">客户列表</p>
              <h2>全部客户</h2>
            </div>
            <div className="pagination">
              <button onClick={() => changePage(pagination.page - 1)} disabled={pagination.page <= 1 || loading}>
                上一页
              </button>
              <span>
                第 {pagination.page} / {pagination.total_pages || 1} 页（共 {pagination.total} 条）
              </span>
              <button
                onClick={() => changePage(pagination.page + 1)}
                disabled={pagination.page >= (pagination.total_pages || 1) || loading}
              >
                下一页
              </button>
            </div>
          </div>

          <div className="table-wrapper">
            {loading ? (
              <div className="muted">加载中...</div>
            ) : hasCustomers ? (
              <table>
                <thead>
                  <tr>
                    <th>姓名</th>
                    <th>电话</th>
                    <th>性别</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.map((customer) => (
                    <tr key={customer.id}>
                      <td>{customer.name}</td>
                      <td>{customer.phone}</td>
                      <td>{customer.gender === "male" ? "男" : "女"}</td>
                      <td>{formatDate(customer.created_at)}</td>
                      <td className="actions">
                        <button onClick={() => handleView(customer.id)}>查看</button>
                        <button onClick={() => handleEdit(customer)}>编辑</button>
                        <button className="danger" onClick={() => handleDelete(customer.id)}>
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="muted">暂无客户数据，先添加一条吧。</div>
            )}
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <div>
            <p className="eyebrow">详情</p>
            <h2>客户资料</h2>
          </div>
          {viewing && <span className="pill subtle">ID: {viewing.id}</span>}
        </div>
        {viewing ? (
          <div className="detail-grid">
            <DetailItem label="姓名" value={viewing.name} />
            <DetailItem label="联系电话" value={viewing.phone} />
            <DetailItem label="性别" value={viewing.gender === "male" ? "男" : "女"} />
            <DetailItem label="创建时间" value={formatDate(viewing.created_at)} />
            <DetailItem label="更新时间" value={formatDate(viewing.updated_at)} />
          </div>
        ) : (
          <div className="muted">选择一条记录查看详情。</div>
        )}
      </section>
    </div>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="detail-item">
      <span className="label">{label}</span>
      <span className="value">{value || "-"}</span>
    </div>
  );
}
