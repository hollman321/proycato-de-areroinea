"use client";

import { ReactQueryProvider } from "@/providers/ReactQueryProvider";
import { ToastProvider } from "@/providers/ToastProvider";
import React from "react";

export default function ClientProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ReactQueryProvider>
      <ToastProvider>{children}</ToastProvider>
    </ReactQueryProvider>
  );
}
