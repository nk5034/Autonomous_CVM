import type { Metadata } from "next";
import { Manrope, Oswald } from "next/font/google";

import "./globals.css";

const heading = Oswald({ subsets: ["latin"], variable: "--font-heading", weight: ["400", "500", "600"] });
const body = Manrope({ subsets: ["latin"], variable: "--font-body" });

export const metadata: Metadata = {
  title: "CVM Catalyst Enterprise",
  description: "Enterprise campaign management control plane",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${heading.variable} ${body.variable}`}>
      <body>{children}</body>
    </html>
  );
}
