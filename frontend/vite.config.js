import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

/** @type {import('vite').UserConfig} */
export default ({ mode }) => {
    process.env = {...process.env, ...loadEnv(mode, process.cwd())};
    return defineConfig({
        server: {
            host: '0.0.0.0',
            port: 8080,
        },
        plugins: [sveltekit()]
    });
}
