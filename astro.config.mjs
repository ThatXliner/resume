import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import icon from "astro-icon";

import svelte from "@astrojs/svelte";

// https://astro.build/config
export default defineConfig({
  site: "https://thatxliner.github.io",
  base: "/resume",
  integrations: [tailwind(), icon(), svelte()]
});