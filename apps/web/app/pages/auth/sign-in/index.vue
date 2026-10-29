<script setup lang="ts">
    import { ArrowLeft, Home } from "lucide-vue-next";
    import { toast } from "vue-sonner";

    definePageMeta({
        title: "auth.sign_in.title",
        auth: { unauthenticatedOnly: true, navigateAuthenticatedTo: "/" },
        middleware: ["propagate-callback-url"],
        i18n: {
            paths: {
                en: "/auth/sign-in",
                es: "/authenticacion/iniciar-sesion",
            },
        },
    });

    const { locale } = useI18n();
    const runtimeConfig = useRuntimeConfig();

    useSeoMeta({
        description: () => $t("auth.sign_in.subtitle"),

        ogImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,
        twitterImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,

        ogType: "website",
        ogTitle: () => $t("auth.sign_in.title"),
        ogDescription: () => $t("auth.sign_in.subtitle"),
        ogLocale: () => locale.value.replace("-", "_"),
        ogSiteName: () => $t("layouts.title"),

        twitterCard: "summary_large_image",
        twitterTitle: () => $t("auth.sign_in.title"),
        twitterDescription: () => $t("auth.sign_in.subtitle"),

        robots: "noindex, follow",
    });

    const { $localeRoute } = useNuxtApp();
    const { navigate } = useCallbackUrl();

    function handleSuccess(email: string) {
        toast.success($t("auth.events.user_logged.title"), {
            description: $t("auth.events.user_logged.description", {
                email,
            }),
        });

        navigate();
    }

    const errorToast = useErrorToast();
    function handleError(error: string) {
        errorToast.handle(error);
    }
</script>

<template>
    <div class="flex flex-col min-h-svh items-center justify-center px-4 py-12">
        <div class="w-full max-w-md overflow-hidden space-y-2">
            <Card>
                <CardHeader class="items-center px-6 pt-8 pb-4 text-center sm:px-8">
                    <CardTitle
                        class="text-center font-mono text-3xl font-bold tracking-[0.2em] text-foreground sm:text-4xl"
                    >
                        {{ $t("layouts.title") }}
                    </CardTitle>
                    <CardDescription class="w-full pt-3 text-center">
                        <h2 class="text-xl font-semibold uppercase tracking-wide text-foreground">
                            {{ $t("auth.sign_in.title") }}
                        </h2>
                        <p class="mt-2 text-sm text-muted-foreground">
                            {{ $t("auth.sign_in.subtitle") }}
                        </p>
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <AuthSignInForm @success="handleSuccess" @error="handleError" />
                </CardContent>
            </Card>
            <div class="flex justify-between space-x-2">
                <div class="flex space-x-2">
                    <Button variant="outline" class="cursor-pointer" @click="$router.back()">
                        <ArrowLeft />
                    </Button>
                    <Button variant="outline" as-child>
                        <NuxtLink :to="$localeRoute({ name: 'index' })">
                            <Home />
                        </NuxtLink>
                    </Button>
                </div>
                <div class="flex space-x-2">
                    <SettingsLocale />
                    <SettingsColorMode :content-props="{ side: 'bottom', align: 'end' }" />
                </div>
            </div>
        </div>
    </div>
</template>
