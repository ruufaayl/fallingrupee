import "@fontsource/instrument-serif/400.css";
import "@fontsource/instrument-serif/400-italic.css";
import "@fontsource-variable/inter";
import "@fontsource-variable/jetbrains-mono";
import "@fontsource-variable/fraunces";
import "./globals.css";

import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

const description =
  "An econometric investigation of exchange-rate depreciation, international food prices and food inflation in Pakistan, 2015–2025: ARDL bounds testing and a nonlinear ARDL test of whether depreciation and appreciation pass through to food prices symmetrically.";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://the-price-of-a-falling-rupee.vercel.app"),
  title: {
    default: "The Price of a Falling Rupee — Pakistan's Food Inflation Crisis",
    template: "%s · The Price of a Falling Rupee",
  },
  description,
  keywords: [
    "Pakistan",
    "food inflation",
    "exchange rate pass-through",
    "NARDL",
    "ARDL bounds test",
    "asymmetric pass-through",
    "PKR",
    "macroeconomics",
    "econometrics",
  ],
  authors: [{ name: "Macroeconomics Final Semester Project" }],
  openGraph: {
    type: "article",
    title: "The Price of a Falling Rupee",
    description,
    locale: "en_GB",
  },
  twitter: { card: "summary_large_image", title: "The Price of a Falling Rupee", description },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#0b0c0e",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a
          href="#problem"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-sm focus:bg-paper focus:px-4 focus:py-2 focus:text-ink"
        >
          Skip to the investigation
        </a>
        {children}
      </body>
    </html>
  );
}
