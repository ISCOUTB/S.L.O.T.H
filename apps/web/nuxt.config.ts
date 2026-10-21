import process from "node:process";
import tailwindcss from "@tailwindcss/vite";
import Sonda from "sonda/nuxt";
import { nodePolyfills } from "vite-plugin-node-polyfills";

export default defineNuxtConfig({
    compatibilityDate: "2025-07-15",
    devtools: {
        enabled: true,
        timeline: {
            enabled: true,
        },
    },

    ///////////////////////////////////////////////////////
    // CORE CONFIG
    ///////////////////////////////////////////////////////
    css: ["~/assets/css/tailwind.css"],
    vite: {
        plugins: [
            tailwindcss(),
            {
                ...nodePolyfills({
                    globals: {
                        process: true,
                        Buffer: true,
                        global: true,
                    },
                }),
                apply(_, { isSsrBuild }) {
                    return !isSsrBuild;
                },
            },
        ],
        optimizeDeps: {
            include: [
                "zod",
                "xlsx",
                "lucide-vue-next",
                "reka-ui",
                "gsap",
                "gsap/all",
                "clsx",
                "tailwind-merge",
                "file-type",
                "uuid",
                "ajv", // CJS
                "class-variance-authority",
                "vaul-vue",
                "knex", // CJS
                "filesize",
            ],
        },
        server: {
            allowedHosts: [".trycloudflare.com"],
            watch: {
                usePolling: true,
                interval: 1000,
            },
            hmr: {
                overlay: false,
            },
        },
    },
    modules: [
        "@nuxt/eslint",
        "@vite-pwa/nuxt",
        "@nuxtjs/i18n",
        "@nuxt/image",
        "@nuxtjs/color-mode",
        "@vueuse/nuxt",
        "@sidebase/nuxt-auth",
        "@vee-validate/nuxt",
        "@nuxtjs/seo",
        "shadcn-nuxt",
        "@artmizu/nuxt-prometheus",
        "vue-sonner/nuxt",
        Sonda({ server: true, open: false, filename: "sonda_[env]", gzip: true }),
    ],
    imports: {
        dirs: [
            "~/composables/**/!(*test|*.spec).{ts,js,mjs,mts}",
            "~/utils/**/!(*test|*.spec).{ts,js,mjs,mts}",
            "~~/shared/utils/**/!(*test|*.spec).{ts,js,mjs,mts}",
        ],
    },
    components: [
        { path: "~/components/", extensions: [".vue"] },
        { path: "~/components/common", pathPrefix: false, extensions: [".vue"] },
    ],
    ignore: ["**/*.test.ts", "**/*.spec.ts"],
    runtimeConfig: {
        auth: {
            SECRET: process.env.AUTH_SECRET,
            SIGN: process.env.AUTH_SIGN,
            MAX_AGE: 30 * 24 * 60 * 60,
        },
        public: {
            API_BASE: process.env.API_BASE_URL,
            i18n: {
                baseUrl: process.env.NUXT_SITE_URL,
            },
            services: {
                ai: !!(process.env.MODEL_API_KEY && process.env.MODEL_ENDPOINT),
                auth: {
                    signUp: true,
                    signIn: true,
                },
            },
        },
        keys: {
            MODEL_API_KEY: process.env.MODEL_API_KEY,
            MODEL_ENDPOINT: process.env.MODEL_ENDPOINT,
        },
        database: {
            default: {
                HOST: process.env.DEFAULT_PROJECT_POSTGRES_HOST,
                PORT: process.env.DEFAULT_PROJECT_POSTGRES_PORT,
                USER: process.env.DEFAULT_PROJECT_POSTGRES_USER,
                PASSWORD: process.env.DEFAULT_PROJECT_POSTGRES_PASSWORD,
                DB: process.env.DEFAULT_PROJECT_POSTGRES_DB,
            },
            redis: {
                HOST: process.env.REDIS_HOST,
                PORT: process.env.REDIS_PORT,
                PASSWORD: process.env.REDIS_PASSWORD,
                DB: process.env.REDIS_DB,
                MAX_RETRIES: process.env.REDIS_MAX_RETRIES,
                BACKOFF_FACTOR: process.env.REDIS_RETRY_BACKOFF_FACTOR,
            },
        },
    },

    ///////////////////////////////////////////////////////
    // MODULES CONFIG
    ///////////////////////////////////////////////////////
    eslint: { config: { standalone: false } },
    shadcn: {
        prefix: "",
        componentDir: "@/components/ui",
    },
    colorMode: {
        classSuffix: "",
    },
    i18n: {
        skipSettingLocaleOnNavigate: false,
        detectBrowserLanguage: {
            useCookie: true,
            redirectOn: "no prefix",
            fallbackLocale: "en",
            alwaysRedirect: true,
        },
        customRoutes: "meta",
        defaultLocale: "en",
        strategy: "prefix",
        locales: [
            {
                code: "en",
                language: "en-US",
                file: "en.json",
                name: "English",
            },
            {
                code: "es",
                language: "es-ES",
                file: "es.json",
                name: "Español",
            },
        ],
        autoDeclare: true,
        experimental: {
            typedPages: true,
        },
    },
    pwa: {
        registerType: "autoUpdate",
        manifest: {
            name: "S.L.O.T.H",
            short_name: "S.L.O.T.H",
            description: "Graphical Interface for S.L.O.T.H Framework",
            theme_color: "#000",
            background_color: "#000",
            display: "standalone",
            display_override: ["window-controls-overlay"],
            start_url: "/?standalone=true",
            scope: "/",
            icons: [
                {
                    src: "/icon-512x512.png",
                    sizes: "512x512",
                    type: "image/png",
                },
                {
                    src: "/icon-192x192.png",
                    sizes: "192x192",
                    type: "image/png",
                },
            ],
            screenshots: [],
        },
        workbox: {
            cleanupOutdatedCaches: true,
            clientsClaim: true,
            maximumFileSizeToCacheInBytes: 10 * 1024 * 1024,
            globPatterns: ["**/*.{js,css,html,png,svg,ico}"],
            globIgnores: ["**/_payload.json", "_nuxt/builds/**/*.json", "sw.js", "workbox-*.js"],
            runtimeCaching: [
                {
                    urlPattern: ({ request }) => request.mode === "navigate",
                    handler: "NetworkFirst",
                    options: {
                        cacheName: "pages-cache",
                        networkTimeoutSeconds: 3,
                        cacheableResponse: { statuses: [0, 200] },
                    },
                },
                {
                    urlPattern: /\.(?:js|css|webmanifest|json)$/,
                    handler: "StaleWhileRevalidate",
                    options: {
                        cacheName: "static-resources",
                    },
                },
            ],
        },
    },
    auth: {
        baseURL: process.env.AUTH_ORIGIN,
        provider: {
            type: "authjs",
        },
        sessionRefresh: {
            enablePeriodically: 5 * 60 * 1000,
            enableOnWindowFocus: true,
        },
    },
    veeValidate: {
        autoImports: true,
        componentNames: {
            Field: "VeeField",
            FieldArray: "VeeFieldArray",
            Form: "VeeForm",
            ErrorMessage: "VeeErrorMessage",
        },
    },
    sitemap: {
        exclude: ["/test/**", "/auth/**"],
        zeroRuntime: true,
    },

    ///////////////////////////////////////////////////////
    // ENVIRONMENT
    ///////////////////////////////////////////////////////
    $development: {
        debug: true,
        sourcemap: true,
    },
    $production: {
        sourcemap: false,
        site: {
            indexable: true,
        },
        nitro: {
            prerender: {
                routes: ["/robots.txt", "/sitemap.xml"],
            },
        },
    },

    ///////////////////////////////////////////////////////
    // NITRO & FLAGS
    ///////////////////////////////////////////////////////
    experimental: {
        payloadExtraction: false,
        appManifest: false,
        scanPageMeta: true,
    },
    nitro: {
        experimental: {
            websocket: true,
        },
        externals: {
            inline: ["xlsx"],
        },
        imports: {
            dirs: ["./shared/utils/**/!(*test|*.spec).{ts,js,mjs,mts}"],
        },
        devProxy: {
            "/sw.js": { target: "/sw.js" },
        },
    },
});
