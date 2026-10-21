<script setup lang="ts">
    import {
        ArrowRight,
        Database,
        FileJson,
        FolderKanban,
        GitBranch,
        Shield,
        Zap,
    } from "lucide-vue-next";

    definePageMeta({
        layout: "sidebar",
        i18n: {
            paths: {
                en: "/",
            },
        },
        breadcrumb: {
            label: "home.title",
        },
    });

    export interface Feature {
        icon: Components.LucideIconComponent;
        title: string;
        description: string;
    }

    export interface ProjectPreview {
        name: string;
        provider: string;
        tables: number;
        tablesLabel: string;
    }

    const { locale } = useI18n();
    const runtimeConfig = useRuntimeConfig();

    useSeoMeta({
        title: () => `${$t("layouts.title")}: ${$t("layouts.tagline")}`,
        description: () => $t("layouts.description"),

        ogImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,
        twitterImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,

        ogType: "website",
        ogTitle: () => `${$t("layouts.title")}: ${$t("layouts.tagline")}`,
        ogDescription: () => $t("layouts.description"),
        ogLocale: () => locale.value.replace("-", "_"),
        ogSiteName: () => $t("layouts.title"),

        twitterCard: "summary_large_image",
        twitterTitle: () => `${$t("layouts.title")}: ${$t("layouts.tagline")}`,
        twitterDescription: () => $t("layouts.description"),

        robots: "index, follow",
    });

    const features: Feature[] = [
        {
            icon: Database,
            title: "home.features.native_support.title",
            description: "home.features.native_support.description",
        },
        {
            icon: FileJson,
            title: "home.features.jsonb_validation.title",
            description: "home.features.jsonb_validation.description",
        },
        {
            icon: Shield,
            title: "home.features.type_integrity.title",
            description: "home.features.type_integrity.description",
        },
        {
            icon: FolderKanban,
            title: "home.features.schema_organization.title",
            description: "home.features.schema_organization.description",
        },
        {
            icon: GitBranch,
            title: "home.features.versioning.title",
            description: "home.features.versioning.description",
        },
        {
            icon: Zap,
            title: "home.features.one_click_import.title",
            description: "home.features.one_click_import.description",
        },
    ];

    const previewProjects: ProjectPreview[] = [
        {
            name: "home.preview_projects.production_main.name",
            provider: "home.preview_projects.production_main.provider",
            tables: 24,
            tablesLabel: "home.preview_projects.tables_label",
        },
        {
            name: "home.preview_projects.analytics_replica.name",
            provider: "home.preview_projects.analytics_replica.provider",
            tables: 18,
            tablesLabel: "home.preview_projects.tables_label",
        },
        {
            name: "home.preview_projects.staging_dev.name",
            provider: "home.preview_projects.staging_dev.provider",
            tables: 12,
            tablesLabel: "home.preview_projects.tables_label",
        },
    ];

    const routeError = useRouteError();
    onMounted(() => routeError.onToast());
</script>

<template>
    <div class="flex min-h-screen flex-col bg-background">
        <main class="flex-1">
            <section class="relative overflow-hidden">
                <div
                    class="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,var(--tw-gradient-stops))] from-muted/50 via-background to-background"
                />
                <div class="mx-auto max-w-6xl px-4 py-24 md:py-32">
                    <div class="mx-auto max-w-3xl text-center">
                        <Badge variant="secondary" class="mb-4">
                            {{ $t("home.hero.badge") }}
                        </Badge>
                        <h1
                            class="text-balance text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl"
                        >
                            {{ $t("home.hero.title_prefix") }}
                            <span class="text-primary">{{ $t("home.hero.title_accent") }}</span>
                        </h1>
                        <p class="mx-auto mt-6 max-w-2xl text-pretty text-lg text-muted-foreground">
                            {{ $t("home.hero.description", { app: $t("layouts.title") }) }}
                        </p>
                        <div
                            class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
                        >
                            <Button size="lg" as-child>
                                <NuxtLink :to="$localeRoute({ name: 'projects-create' })">
                                    {{ $t("home.hero.cta") }}
                                    <ArrowRight class="ml-2 size-4" />
                                </NuxtLink>
                            </Button>
                        </div>
                    </div>

                    <div class="mx-auto mt-16 max-w-4xl">
                        <div class="overflow-hidden rounded-xl border bg-card shadow-2xl">
                            <div class="flex items-center gap-2 border-b bg-muted/50 px-4 py-3">
                                <div class="size-3 rounded-full bg-red-500/80" />
                                <div class="size-3 rounded-full bg-yellow-500/80" />
                                <div class="size-3 rounded-full bg-green-500/80" />
                                <span class="ml-2 text-xs text-muted-foreground">
                                    {{ $t("layouts.title") }} -
                                    {{ $t("home.preview_projects.window_title") }}
                                </span>
                            </div>
                            <div class="grid gap-4 p-6 md:grid-cols-3">
                                <div
                                    v-for="project in previewProjects"
                                    :key="project.name"
                                    class="rounded-lg border bg-background p-4 transition-colors hover:border-primary/50"
                                >
                                    <div class="flex items-center gap-3">
                                        <div
                                            class="flex size-9 items-center justify-center rounded-lg bg-primary/10"
                                        >
                                            <Database class="size-4 text-primary" />
                                        </div>
                                        <div>
                                            <p class="text-sm font-medium">
                                                {{ $t(project.name) }}
                                            </p>
                                            <p class="text-xs text-muted-foreground">
                                                {{ $t(project.provider) }}
                                            </p>
                                        </div>
                                    </div>
                                    <div
                                        class="mt-3 flex items-center justify-between text-xs text-muted-foreground"
                                    >
                                        <span>
                                            {{
                                                $t(project.tablesLabel, {
                                                    count: project.tables,
                                                })
                                            }}
                                        </span>
                                        <Badge variant="outline" class="text-[10px]">
                                            {{ $t("home.preview_projects.connected") }}
                                        </Badge>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <Separator />

            <section id="features" class="py-24">
                <div class="mx-auto max-w-6xl px-4">
                    <div class="mx-auto max-w-2xl text-center">
                        <h2 class="text-balance text-3xl font-bold tracking-tight md:text-4xl">
                            {{ $t("home.features.title") }}
                        </h2>
                        <p class="mt-4 text-muted-foreground">
                            {{ $t("home.features.description", { app: $t("layouts.title") }) }}
                        </p>
                    </div>

                    <div class="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                        <div
                            v-for="feature in features"
                            :key="feature.title"
                            class="group rounded-xl border bg-card p-6 transition-colors hover:border-primary/50"
                        >
                            <div
                                class="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground"
                            >
                                <component :is="feature.icon" class="size-5" />
                            </div>
                            <h3 class="mt-4 font-semibold">{{ $t(feature.title) }}</h3>
                            <p class="mt-2 text-sm text-muted-foreground">
                                {{ $t(feature.description) }}
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <Separator />

        <footer class="py-12">
            <div class="mx-auto max-w-6xl px-4">
                <div class="flex flex-col items-center justify-between gap-6 md:flex-row">
                    <div class="flex items-center gap-2">
                        <div
                            class="flex size-6 items-center justify-center rounded bg-primary text-primary-foreground"
                        >
                            <Database class="size-3" />
                        </div>
                        <span class="text-sm font-semibold">{{ $t("layouts.title") }}</span>
                    </div>
                    <p class="text-sm text-muted-foreground">
                        {{ $t("home.footer.copyright", { app: $t("layouts.title") }) }}
                    </p>
                </div>
            </div>
        </footer>
    </div>
</template>
