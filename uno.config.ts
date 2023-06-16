// uno.config.ts
import { defineConfig } from 'unocss';
import { presetUno } from 'unocss';
import { presetDaisy } from 'unocss-preset-daisy';
import extractorSvelte from '@unocss/extractor-svelte';

export default defineConfig({
	presets: [presetUno(), presetDaisy()],
	extractors: [extractorSvelte()]
});
