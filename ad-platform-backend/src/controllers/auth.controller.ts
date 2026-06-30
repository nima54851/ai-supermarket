import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { prisma } from '../index';
import { AppError } from '../middleware/errorHandler';

interface RegisterBody {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
}

interface LoginBody {
  email: string;
  password: string;
}

export const register = async (req: Request, res: Response) => {
  try {
    const { email, password, username, full_name }: RegisterBody = req.body;

    // Validation
    if (!email || !password) {
      throw new AppError('Email and password are required', 400);
    }

    if (password.length < 8) {
      throw new AppError('Password must be at least 8 characters', 400);
    }

    // Check if user already exists
    const existingUser = await prisma.user.findFirst({
      where: {
        OR: [
          { email },
          ...(username ? [{ username }] : []),
        ],
      },
    });

    if (existingUser) {
      throw new AppError('User already exists', 409);
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const password_hash = await bcrypt.hash(password, salt);

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        username,
        full_name,
        password_hash,
      },
      select: {
        id: true,
        email: true,
        username: true,
        full_name: true,
        role: true,
        created_at: true,
      },
    });

    // Create audit log
    await prisma.auditLog.create({
      data: {
        action: 'REGISTER',
        entity: 'User',
        entity_id: user.id,
        new_data: JSON.stringify({
          email: user.email,
          username: user.username,
        }),
      },
    });

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: user,
    });
  } catch (error) {
    throw error;
  }
};

export const login = async (req: Request, res: Response) => {
  try {
    const { email, password }: LoginBody = req.body;

    if (!email || !password) {
      throw new AppError('Email and password are required', 400);
    }

    // Find user
    const user = await prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      throw new AppError('Invalid credentials', 401);
    }

    if (!user.is_active) {
      throw new AppError('Account is deactivated', 403);
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
      throw new AppError('Invalid credentials', 401);
    }

    // Create JWT tokens
    const accessToken = jwt.sign(
      { userId: user.id },
      process.env.JWT_SECRET!,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    const refreshToken = jwt.sign(
      { userId: user.id, type: 'refresh' },
      process.env.JWT_REFRESH_SECRET!,
      { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '30d' }
    );

    // Create session
    await prisma.session.create({
      data: {
        user_id: user.id,
        token: refreshToken,
        user_agent: req.headers['user-agent'] || undefined,
        ip_address: req.ip || undefined,
        expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
      },
    });

    // Clean up expired sessions
    await prisma.session.deleteMany({
      where: {
        expires_at: { lt: new Date() },
      },
    });

    // Create audit log
    await prisma.auditLog.create({
      data: {
        user_id: user.id,
        action: 'LOGIN',
        entity: 'User',
        entity_id: user.id,
        ip_address: req.ip || undefined,
        user_agent: req.headers['user-agent'] || undefined,
      },
    });

    // Return user info without password
    const userResponse = {
      id: user.id,
      email: user.email,
      username: user.username,
      full_name: user.full_name,
      role: user.role,
      avatar_url: user.avatar_url,
      membership_type: user.membership_type,
      membership_end: user.membership_end,
      created_at: user.created_at,
    };

    res.status(200).json({
      success: true,
      message: 'Login successful',
      data: {
        user: userResponse,
        tokens: {
          accessToken,
          refreshToken,
          expiresIn: 7 * 24 * 60 * 60, // 7 days in seconds
        },
      },
    });
  } catch (error) {
    throw error;
  }
};

export const logout = async (req: Request, res: Response) => {
  try {
    const refreshToken = req.body.refreshToken;

    if (refreshToken) {
      // Delete session
      await prisma.session.deleteMany({
        where: { token: refreshToken },
      });
    }

    // Create audit log if user is authenticated
    if (req.user) {
      await prisma.auditLog.create({
        data: {
          user_id: req.user.id,
          action: 'LOGOUT',
          entity: 'User',
          entity_id: req.user.id,
          ip_address: req.ip || undefined,
          user_agent: req.headers['user-agent'] || undefined,
        },
      });
    }

    res.status(200).json({
      success: true,
      message: 'Logout successful',
    });
  } catch (error) {
    throw error;
  }
};

export const refreshToken = async (req: Request, res: Response) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      throw new AppError('Refresh token is required', 400);
    }

    // Verify refresh token
    let decoded;
    try {
      decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET!) as {
        userId: string;
        type: string;
      };
    } catch (error) {
      throw new AppError('Invalid refresh token', 401);
    }

    if (decoded.type !== 'refresh') {
      throw new AppError('Invalid token type', 401);
    }

    // Check if session exists
    const session = await prisma.session.findUnique({
      where: { token: refreshToken },
      include: { user: true },
    });

    if (!session || session.expires_at < new Date()) {
      throw new AppError('Session expired', 401);
    }

    if (!session.user.is_active) {
      throw new AppError('Account is deactivated', 403);
    }

    // Generate new access token
    const newAccessToken = jwt.sign(
      { userId: session.user.id },
      process.env.JWT_SECRET!,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    res.status(200).json({
      success: true,
      data: {
        accessToken: newAccessToken,
        expiresIn: 7 * 24 * 60 * 60, // 7 days in seconds
      },
    });
  } catch (error) {
    throw error;
  }
};

export const getProfile = async (req: Request, res: Response) => {
  try {
    // User is already attached by auth middleware
    const user = req.user;

    // Get user's recent stats
    const adCount = await prisma.ad.count({
      where: { user_id: user.id },
    });

    const activeAdCount = await prisma.ad.count({
      where: {
        user_id: user.id,
        status: 'active',
      },
    });

    const totalSpend = await prisma.ad.aggregate({
      where: { user_id: user.id },
      _sum: { spent: true },
    });

    res.status(200).json({
      success: true,
      data: {
        user,
        stats: {
          total_ads: adCount,
          active_ads: activeAdCount,
          total_spend: totalSpend._sum.spent || 0,
        },
      },
    });
  } catch (error) {
    throw error;
  }
};