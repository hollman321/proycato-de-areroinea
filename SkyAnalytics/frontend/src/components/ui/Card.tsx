"use client";

import { cn } from "@/lib/utils";
import { HTMLMotionProps, motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { forwardRef, ReactNode } from "react";

// ===================================================
// BUTTON COMPONENT - Componente de botón reutilizable
// ===================================================

interface ButtonProps extends Omit<
  HTMLMotionProps<"button">,
  "ref" | "children"
> {
  children?: ReactNode;
  variant?: "primary" | "secondary" | "ghost" | "danger" | "success";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className,
      variant = "primary",
      size = "md",
      loading = false,
      icon,
      disabled,
      ...props
    },
    ref,
  ) => {
    const variants = {
      primary:
        "bg-sky-500 hover:bg-sky-600 text-white shadow-lg shadow-sky-500/25",
      secondary: "bg-slate-700 hover:bg-slate-600 text-white",
      ghost: "bg-transparent hover:bg-white/10 text-slate-300 hover:text-white",
      danger:
        "bg-rose-500 hover:bg-rose-600 text-white shadow-lg shadow-rose-500/25",
      success:
        "bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/25",
    };

    const sizes = {
      sm: "px-3 py-1.5 text-xs gap-1.5",
      md: "px-4 py-2.5 text-sm gap-2",
      lg: "px-6 py-3 text-base gap-2.5",
    };

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
        whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
        className={cn(
          "inline-flex items-center justify-center rounded-xl font-semibold transition-all duration-200",
          "focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-900",
          variants[variant],
          sizes[size],
          (disabled || loading) && "opacity-50 cursor-not-allowed",
          className,
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : icon ? (
          <span className="flex-shrink-0">{icon}</span>
        ) : null}
        {children}
      </motion.button>
    );
  },
);

Button.displayName = "Button";
