// @ts-check
import { defineConfig, fontProviders } from "astro/config";

import tailwindcss from "@tailwindcss/vite";

import react from "@astrojs/react";

import icon from "astro-icon";

// https://astro.build/config
export default defineConfig({
  site: "https://thatxliner.github.io",
  base: "/resume",
  vite: {
    plugins: [tailwindcss()],
  },

  integrations: [react(), icon()],
  // experimental: {
  //   fonts: [
  //     {
  //       name: "Inter",
  //       cssVariable: "--font-inter",
  //       provider: fontProviders.fontsource(),
  //       // Specify weights that are actually used
  //       weights: [100],
  //       // Specify styles that are actually used
  //       styles: ["normal"],
  //       // Download only font files for characters used on the page
  //       subsets: ["latin"],
  //     },
  //   ],
  // },
});
