import type { UseWebSocketReturn } from "@vueuse/core";
import type { ConsolaInstance } from "consola";
import type { gsap } from "gsap";
import type { $Fetch, NitroFetchRequest } from "nitropack";
import type { RuntimeConfig } from "nuxt/schema";
import "vue-router";

// source: @sidebase/nuxt-auth/dist/runtime/middleware/sidebase-auth.d.ts
type AuthMiddlewareMeta =
    | boolean
    | {
        /**
         * Whether to allow only unauthenticated users to access this page.
         *
         * Authenticated users will be redirected to `/` or the route defined in `navigateAuthenticatedTo`
         */
        unauthenticatedOnly: boolean;
        /**
         * Where to redirect authenticated users if `unauthenticatedOnly` is set to true
         *
         * @default undefined
         */
        navigateAuthenticatedTo?: string;
        /**
         * Where to redirect unauthenticated users if this page is protected
         *
         * @default undefined
         */
        navigateUnauthenticatedTo?: string;
    };

interface PageMetaEvents { }

declare module "#app" {
    interface NuxtApp {
        $socket: UseWebSocketReturn<WebSocket.Message>;
        $gsap: typeof gsap;
        $api: $Fetch<unknown, NitroFetchRequest>;
        $logger: ConsolaInstance;
    }

    interface PageMeta {
        title?: string;
        auth?: AuthMiddlewareMeta;
        breadcrumb?: Breadcrumb.PageMeta;
        events?: Partial<PageMetaEvents>;
        services?: DotNotation<RuntimeConfig["public"]["services"]>[];
    }
}

declare module "vue" {
    interface ComponentCustomProperties {
        $socket: UseWebSocketReturn<WebSocket.Message>;
        $gsap: typeof gsap;
        $api: $Fetch<unknown, NitroFetchRequest>;
        $logger: ConsolaInstance;
    }
}

declare module "vue-router" {
    interface RouteMeta {
        title?: string;
        auth?: AuthMiddlewareMeta;
        breadcrumb?: Breadcrumb.PageMeta;
        events?: Partial<PageMetaEvents>;
        services?: DotNotation<RuntimeConfig["services"]>[];
    }
}
