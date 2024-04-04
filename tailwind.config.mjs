import daisyui from "daisyui";
import typography from "@tailwindcss/typography";
import * as icon from "@egoist/tailwindcss-icons";
const { iconsPlugin, getIconCollections } = icon;
/** @type {import('tailwindcss').Config} */
export default {
	content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
	theme: {
		extend: {},
	},
	plugins: [
		daisyui,
		iconsPlugin({
			collections: getIconCollections(["mdi"]),
		}),
		typography,
	],
	daisyui: { themes: ["light", "dark"] },
};
