import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Proctoring System",
  description: "Secure and intelligent exam proctoring",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
