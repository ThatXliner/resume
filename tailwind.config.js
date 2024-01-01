import daisyui from 'daisyui';
import * as icon from '@egoist/tailwindcss-icons';
const { iconsPlugin, getIconCollections } = icon;
/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {}
	},
	plugins: [
		daisyui,
		iconsPlugin({
			collections: getIconCollections(['mdi'])
		})
	],
	daisyui: { themes: ['light'] }
};
