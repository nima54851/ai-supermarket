import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';
import { createServer } from 'http';
import { Server } from 'socket.io';

// Load environment variables
dotenv.config();

// Import routes
import authRoutes from './routes/auth.routes';
import userRoutes from './routes/user.routes';
import adRoutes from './routes/ad.routes';
import paymentRoutes from './routes/payment.routes';
import adminRoutes from './routes/admin.routes';
import analyticsRoutes from './routes/analytics.routes';

// Import middleware
import { errorHandler } from './middleware/errorHandler';
import { authMiddleware } from './middleware/auth';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
    credentials: true,
  },
});

// Prisma client
export const prisma = new PrismaClient();

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true,
}));
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
  });
});

// API Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/users', authMiddleware, userRoutes);
app.use('/api/v1/ads', authMiddleware, adRoutes);
app.use('/api/v1/payments', authMiddleware, paymentRoutes);
app.use('/api/v1/admin', authMiddleware, adminRoutes);
app.use('/api/v1/analytics', authMiddleware, analyticsRoutes);

// WebSocket connection handling
io.on('connection', (socket) => {
  console.log('New client connected:', socket.id);

  socket.on('join:user', (userId: string) => {
    socket.join(`user:${userId}`);
    console.log(`User ${userId} joined their room`);
  });

  socket.on('join:admin', () => {
    socket.join('admin');
    console.log('Admin joined admin room');
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Export socket.io for use in controllers
export { io };

// Error handling middleware
app.use(errorHandler);

const PORT = process.env.PORT || 3000;

// Graceful shutdown
const gracefulShutdown = async () => {
  console.log('Shutting down gracefully...');
  
  // Close socket.io server
  io.close();
  
  // Close HTTP server
  httpServer.close(async () => {
    console.log('HTTP server closed');
    
    // Close Prisma connection
    await prisma.$disconnect();
    console.log('Prisma connection closed');
    
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Start server
httpServer.listen(PORT, () => {
  console.log(`
  🚀 Server is running!
  
  Environment: ${process.env.NODE_ENV}
  Port: ${PORT}
  URL: http://localhost:${PORT}
  
  Health check: http://localhost:${PORT}/health
  API Docs: http://localhost:${PORT}/api-docs (if enabled)
  `);
});

export default app;