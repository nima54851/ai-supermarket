import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { prisma } from '../index';
import { AppError } from './errorHandler';

export interface AuthRequest extends Request {
  user?: any;
}

export const authMiddleware = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    // Get token from header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new AppError('No token provided', 401);
    }

    const token = authHeader.split(' ')[1];

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };

    // Find user in database
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
      select: {
        id: true,
        email: true,
        username: true,
        full_name: true,
        role: true,
        avatar_url: true,
        is_active: true,
        membership_type: true,
        membership_end: true,
        created_at: true,
      },
    });

    if (!user) {
      throw new AppError('User not found', 404);
    }

    if (!user.is_active) {
      throw new AppError('Account is deactivated', 403);
    }

    // Check if membership is still valid
    if (user.membership_end && new Date(user.membership_end) < new Date()) {
      // Membership expired, downgrade to free
      await prisma.user.update({
        where: { id: user.id },
        data: {
          membership_type: 'free',
          membership_end: null,
        },
      });
      user.membership_type = 'free';
      user.membership_end = null;
    }

    // Attach user to request
    req.user = user;

    next();
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      next(new AppError('Invalid token', 401));
    } else if (error instanceof jwt.TokenExpiredError) {
      next(new AppError('Token expired', 401));
    } else {
      next(error);
    }
  }
};

export const adminMiddleware = (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  if (!req.user) {
    throw new AppError('Authentication required', 401);
  }

  if (req.user.role !== 'admin') {
    throw new AppError('Admin access required', 403);
  }

  next();
};

export const premiumMiddleware = (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  if (!req.user) {
    throw new AppError('Authentication required', 401);
  }

  const premiumPlans = ['pro', 'enterprise'];
  if (!premiumPlans.includes(req.user.membership_type)) {
    throw new AppError('Premium membership required', 403);
  }

  next();
};