import { Request, Response, NextFunction } from 'express';
import { Prisma } from '@prisma/client';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  err: Error | AppError | Prisma.PrismaClientKnownRequestError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString(),
  });

  // Default error
  let statusCode = 500;
  let message = 'Internal server error';
  let errors: any[] = [];

  // AppError (operational errors)
  if (err instanceof AppError) {
    statusCode = err.statusCode;
    message = err.message;
  }

  // Prisma errors
  else if (err instanceof Prisma.PrismaClientKnownRequestError) {
    // Handle specific Prisma errors
    switch (err.code) {
      case 'P2002':
        statusCode = 409;
        message = 'Unique constraint violation';
        errors = err.meta?.target as string[] || [];
        break;
      case 'P2025':
        statusCode = 404;
        message = 'Record not found';
        break;
      case 'P2003':
        statusCode = 400;
        message = 'Foreign key constraint violation';
        break;
      default:
        statusCode = 400;
        message = 'Database error';
    }
  }

  // Validation errors (from express-validator)
  else if (err.name === 'ValidationError') {
    statusCode = 400;
    message = 'Validation error';
    errors = (err as any).errors || [];
  }

  // JWT errors
  else if (err.name === 'JsonWebTokenError') {
    statusCode = 401;
    message = 'Invalid token';
  } else if (err.name === 'TokenExpiredError') {
    statusCode = 401;
    message = 'Token expired';
  }

  // Rate limit error
  else if ((err as any).statusCode === 429) {
    statusCode = 429;
    message = 'Too many requests';
  }

  // Response
  res.status(statusCode).json({
    success: false,
    message,
    errors: errors.length > 0 ? errors : undefined,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined,
    timestamp: new Date().toISOString(),
  });
};