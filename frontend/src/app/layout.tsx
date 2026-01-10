import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ToastProvider } from "@/components/ui";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MetaGPT-Pro | Autonomous AI Software Engineering",
  description: "Enterprise AI-powered software development platform with autonomous agents, sprint management, and real-time collaboration.",
  keywords: ["AI", "Software Engineering", "MetaGPT", "Autonomous Agents", "Project Management"],
  authors: [{ name: "MetaGPT-Pro Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <body className={inter.variable}>
        <ToastProvider position="top-right">
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
