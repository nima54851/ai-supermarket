#!/usr/bin/env node
/**
 * CoursePay 完整平台 - 后端服务器
 * 功能：用户管理 + 订单处理 + 邮件通知
 */

const express = require('express');
const mongoose = require('mongoose');
const nodemailer = require('nodemailer');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// 数据库连接
const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/coursepay';
mongoose.connect(mongoURI);

// 用户模型
const UserSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  name: String,
  createdAt: { type: Date, default: Date.now },
  purchases: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Order' }]
});

// 课程模型
const CourseSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: String,
  price: { type: Number, required: true },
  currency: { type: String, default: 'CNY' },
  lessons: [String],
  duration: String,
  status: { type: String, default: 'active' }
});

// 订单模型
const OrderSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  courseId: { type: mongoose.Schema.Types.ObjectId, ref: 'Course' },
  amount: Number,
  currency: String,
  paypalEmail: String,
  transactionId: String,
  status: { type: String, default: 'pending' }, // pending, paid, completed, cancelled
  createdAt: { type: Date, default: Date.now },
  paidAt: Date,
  accessCode: String // 访问课程的唯一代码
});

const User = mongoose.model('User', UserSchema);
const Course = mongoose.model('Course', CourseSchema);
const Order = mongoose.model('Order', OrderSchema);

// 邮件配置
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER || 'your-email@gmail.com',
    pass: process.env.EMAIL_PASS || 'your-password'
  }
});

// ========== API 路由 ==========

// 1. 课程列表
app.get('/api/courses', async (req, res) => {
  try {
    const courses = await Course.find({ status: 'active' });
    res.json({
      success: true,
      data: courses,
      count: courses.length
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 2. 创建订单
app.post('/api/orders', async (req, res) => {
  try {
    const { email, courseId, paypalEmail, transactionId } = req.body;
    
    // 查找或创建用户
    let user = await User.findOne({ email });
    if (!user) {
      user = await User.create({ email, name: email.split('@')[0] });
    }
    
    // 查找课程
    const course = await Course.findById(courseId);
    if (!course) {
      return res.status(404).json({ error: '课程不存在' });
    }
    
    // 生成访问代码
    const accessCode = `COURSE-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
    
    // 创建订单
    const order = await Order.create({
      userId: user._id,
      courseId: course._id,
      amount: course.price,
      currency: course.currency,
      paypalEmail: paypalEmail || 'yinanzo@hotmail.com',
      transactionId,
      status: 'paid',
      paidAt: new Date(),
      accessCode
    });
    
    // 发送邮件
    const mailOptions = {
      from: 'support@coursepay.com',
      to: email,
      subject: `🎉 CoursePay 课程购买成功 - ${course.title}`,
      html: `
        <div style="background:#667eea;color:white;padding:30px;border-radius:15px;">
          <h2>✅ 恭喜！课程购买成功</h2>
          <p><strong>课程:</strong> ${course.title}</p>
          <p><strong>价格:</strong> ${course.price} ${course.currency}</p>
          <p><strong>访问代码:</strong> <code style="background:white;color:#333;padding:10px;border-radius:5px;">${accessCode}</code></p>
          <p><strong>访问链接:</strong> <a href="https://coursepay.com/course/${course._id}?code=${accessCode}" style="color:#00ff9d;">点击这里访问课程</a></p>
          <p>如有问题，请联系: support@coursepay.com</p>
        </div>
      `
    };
    
    // 异步发送邮件（不阻塞响应）
    transporter.sendMail(mailOptions).catch(console.error);
    
    res.json({
      success: true,
      order,
      accessCode,
      message: '订单创建成功！已发送课程访问信息到您的邮箱'
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 3. 验证订单
app.get('/api/orders/:orderId/verify', async (req, res) => {
  try {
    const order = await Order.findById(req.params.orderId)
      .populate('userId', 'email name')
      .populate('courseId', 'title description');
    
    if (!order) {
      return res.status(404).json({ error: '订单不存在' });
    }
    
    res.json({
      success: true,
      order,
      isValid: order.status === 'paid',
      message: order.status === 'paid' ? '订单已验证，可以访问课程' : '订单尚未支付'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 4. 用户订单历史
app.get('/api/users/:email/orders', async (req, res) => {
  try {
    const user = await User.findOne({ email: req.params.email }).populate('purchases');
    
    if (!user) {
      return res.status(404).json({ error: '用户不存在' });
    }
    
    res.json({
      success: true,
      user,
      orders: user.purchases || []
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 5. 课程访问验证
app.post('/api/courses/access', async (req, res) => {
  try {
    const { courseId, accessCode } = req.body;
    
    const order = await Order.findOne({ 
      courseId, 
      accessCode,
      status: 'paid'
    }).populate('courseId');
    
    if (!order) {
      return res.status(403).json({ 
        success: false, 
        error: '访问代码无效或订单未支付' 
      });
    }
    
    res.json({
      success: true,
      course: order.courseId,
      order,
      message: '验证通过，可以访问课程'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 6. 初始化默认课程
app.get('/api/init-courses', async (req, res) => {
  try {
    const defaultCourses = [
      {
        title: "基础编程入门课程",
        description: "适合零基础，30天学会编程",
        price: 99.00,
        currency: "CNY",
        lessons: ["HTML基础", "CSS样式", "JavaScript入门", "项目实战"],
        duration: "30天"
      },
      {
        title: "高级开发技术进阶",
        description: "提升技能，掌握核心框架",
        price: 199.00,
        currency: "CNY", 
        lessons: ["React/Vue框架", "Node.js后端", "数据库设计", "项目部署"],
        duration: "60天"
      },
      {
        title: "全栈开发工程师",
        description: "完整体系，成为全栈开发",
        price: 399.00,
        currency: "CNY",
        lessons: ["前端框架", "后端API", "DevOps", "项目架构"],
        duration: "90天"
      },
      {
        title: "VIP 1对1教学",
        description: "定制课程，快速学习",
        price: 999.00,
        currency: "CNY",
        lessons: ["个性化课程", "实时指导", "项目评审", "职业规划"],
        duration: "自定义"
      }
    ];
    
    await Course.deleteMany({});
    const courses = await Course.insertMany(defaultCourses);
    
    res.json({
      success: true,
      message: `已创建 ${courses.length} 门默认课程`,
      courses
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ========== 前端页面 ==========
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>🎯 CoursePay - 完整平台</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body { margin:0; padding:0; font-family:sans-serif; background:linear-gradient(135deg, #667eea, #764ba2); color:white; }
        .container { max-width:1200px; margin:0 auto; padding:40px; }
        h1 { color:#00ff9d; font-size:3em; text-align:center; }
        .status { background:#00ff9d; color:#333; padding:20px; border-radius:15px; text-align:center; font-size:1.3em; margin:30px 0; }
        .api-list { background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; margin:20px 0; }
        .api-item { margin:10px 0; padding:10px; background:rgba(255,255,255,0.1); border-radius:10px; }
        .btn { background:#00ff9d; color:#333; border:none; padding:12px 24px; border-radius:50px; margin:10px; cursor:pointer; font-weight:bold; }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🚀 CoursePay 完整平台</h1>
        <div class="status">✅ 后端服务器运行中 (端口: ${PORT})</div>
        
        <div class="api-list">
          <h3>📡 API 接口：</h3>
          <div class="api-item"><strong>GET /api/courses</strong> - 获取课程列表</div>
          <div class="api-item"><strong>POST /api/orders</strong> - 创建订单</div>
          <div class="api-item"><strong>GET /api/orders/:id/verify</strong> - 验证订单</div>
          <div class="api-item"><strong>GET /api/users/:email/orders</strong> - 用户订单历史</div>
          <div class="api-item"><strong>POST /api/courses/access</strong> - 课程访问验证</div>
        </div>
        
        <div style="text-align:center; margin-top:40px;">
          <button class="btn" onclick="testAPI()">🧪 测试API</button>
          <button class="btn" onclick="initCourses()">📚 初始化课程</button>
          <button class="btn" onclick="window.open('https://nima54851.github.io/coursepay-simple/', '_blank')">🌐 打开前端页面</button>
        </div>
      </div>
      
      <script>
        async function testAPI() {
          try {
            const res = await fetch('/api/courses');
            const data = await res.json();
            alert('✅ API测试成功！\\n课程数量: ' + data.count);
          } catch(e) {
            alert('❌ API测试失败: ' + e.message);
          }
        }
        
        async function initCourses() {
          try {
            const res = await fetch('/api/init-courses');
            const data = await res.json();
            alert('✅ 课程初始化成功！\\n' + data.message);
          } catch(e) {
            alert('❌ 初始化失败: ' + e.message);
          }
        }
      </script>
    </body>
    </html>
  `);
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 CoursePay 完整平台启动成功！`);
  console.log(`🔗 访问: http://localhost:${PORT}`);
  console.log(`🔗 API: http://localhost:${PORT}/api/courses`);
  console.log(`💰 PayPal收款账户: yinanzo@hotmail.com`);
});

module.exports = app;