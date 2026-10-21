<script setup lang="ts">
    import { FileIcon, Info, Pickaxe, Settings, Table, Upload, User } from "lucide-vue-next";
    import { cn } from "@/lib/utils";

    definePageMeta({
        title: "projects.id.fallback_title",
        layout: "sidebar",
        middleware: ["sidebase-auth", "project-validation"],
        i18n: {
            paths: {
                en: "/projects/[id]",
                es: "/proyectos/[id]",
            },
        },
        breadcrumb: {
            options: {
                parent: {
                    kind: "link",
                },
            },
            overrides: {
                label: {
                    keypath: "PROJECT_TITLE",
                },
            },
        },
    });

    const { locale } = useI18n();
    const runtimeConfig = useRuntimeConfig();
    const { BREADCRUMB_OVERRIDES } = useGlobalState();
    const projectId = useRouteParams("id");
    const setI18nParams = useSetI18nParams();
    setI18nParams({ en: { id: projectId.value } });
    const { VIEWS, project, view, uploadSchema } = useProvideProjectState(
        projectId.value?.toString(),
    );
    useSeoMeta({
        title: () =>
            $t("projects.id.title", {
                projectName: project.value?.name,
            }),
        description: () => $t("projects.id.description"),

        ogImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,
        twitterImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,

        ogType: "website",
        ogTitle: () => $t("projects.id.fallback_title"),
        ogDescription: () => $t("projects.id.description"),
        ogLocale: () => locale.value.replace("-", "_"),
        ogSiteName: () => $t("layouts.title"),

        twitterCard: "summary_large_image",
        twitterTitle: () => $t("projects.id.fallback_title"),
        twitterDescription: () => $t("projects.id.description"),

        robots: "noindex, nofollow",
    });
    watchEffect(() => {
        BREADCRUMB_OVERRIDES.value.PROJECT_TITLE = project.value.name;
    });

    const animations = useViewManagerAnimations();
    const views = useViewManager(
        [
            {
                meta: {
                    label: "projects.id.sections.overview.tab",
                    value: VIEWS.value.Overview.value,
                    icon: Info,
                },
                component: () => import("~/components/project/overview/ProjectOverview.vue"),
                props: {},
            },
            {
                meta: {
                    label: "projects.id.sections.upload_schema.tab",
                    value: VIEWS.value.UploadFile.value,
                    icon: Upload,
                },
                component: () =>
                    import("@/components/project/upload-schema/ProjectUploadSchema.vue"),
                props: {},
            },
            {
                meta: {
                    label: "projects.id.sections.tables.tab",
                    value: VIEWS.value.Tables.value,
                    icon: Table,
                },
                component: () => import("~/components/project/tables/ProjectTables.vue"),
                props: {},
            },
            {
                meta: {
                    label: "projects.id.sections.query_builder.tab",
                    value: VIEWS.value.QueryBuilder.value,
                    icon: Pickaxe,
                },
                component: () =>
                    import("@/components/project/query-builder/ProjectQueryBuilder.vue"),
                props: {},
            },
            {
                meta: {
                    label: "projects.id.sections.settings.tab",
                    value: VIEWS.value.Settings.value,
                    icon: Settings,
                },
                component: () => import("@/components/project/ProjectSettings.vue"),
                props: {},
            },
        ],
        { key: "project-views", model: view },
    );

    watch(
        () => uploadSchema.state.value.uploadedFile,
        (file) => {
            const hasTab = views.computed.filteredViews.value.some(
                (entry) => entry.meta.value === VIEWS.value.File.value,
            );

            if (file && !hasTab) {
                views.dispatch.addView({
                    meta: {
                        label: "projects.id.sections.file.tab",
                        value: VIEWS.value.File.value,
                        icon: FileIcon,
                        class: cn(
                            "relative transition-colors",
                            "data-[state=inactive]:font-semibold data-[state=inactive]:border",
                            "data-[state=active]:ring-2",

                            "data-[state=inactive]:bg-amber-100 data-[state=inactive]:text-amber-900",
                            "data-[state=inactive]:border-amber-300",
                            "data-[state=active]:ring-amber-300/70",

                            "dark:data-[state=inactive]:bg-amber-500/20 dark:data-[state=inactive]:text-amber-100",
                            "dark:data-[state=inactive]:border-amber-400/40",
                            "dark:data-[state=active]:ring-amber-400/40",
                        ),
                    },
                    component: () => import("@/components/project/ProjectFileVisualizer.vue"),
                    props: {},
                });

                return;
            }

            if (!file && hasTab) {
                views.dispatch.removeView(VIEWS.value.File.value);
            }
        },
        { immediate: true },
    );

    const events = useAppEvents();
    onMounted(() => {
        views.dispatch.preload([
            VIEWS.value.UploadFile.value,
            VIEWS.value.Tables.value,
            VIEWS.value.QueryBuilder.value,
        ]);
        events.on("event:projects:change-tab", ({ value }) => views.dispatch.setActive(value));
    });
</script>

<template>
    <div class="mx-auto w-full max-w-5xl">
        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <div class="space-y-1.5">
                    <h1 class="text-2xl font-semibold tracking-tight text-foreground text-balance">
                        {{ project.name }}
                    </h1>
                    <p class="text-sm text-muted-foreground">
                        {{ project.description }}
                    </p>
                </div>

                <AuthRole>
                    <Badge variant="outline">
                        <span>{{ project.owner_user }}</span>
                        <User />
                    </Badge>
                </AuthRole>
            </div>

            <Tabs v-model="view" :default-value="VIEWS.Overview.value">
                <TabsList class="w-full flex-wrap h-full">
                    <TabsTrigger
                        v-for="entry in views.computed.filteredViews.value"
                        :key="entry.meta.value"
                        :value="entry.meta.value"
                        :class="cn('cursor-pointer', entry.meta.class)"
                    >
                        <component :is="entry.meta.icon" v-if="entry.meta.icon" />
                        <span>
                            {{ $t(entry.meta.label) }}
                        </span>
                    </TabsTrigger>
                </TabsList>
                <Transition
                    mode="out-in"
                    :css="false"
                    @enter="animations.onPanelEnter"
                    @leave="animations.onPanelLeave"
                >
                    <TabsContent
                        v-if="views.state.activeView.value && views.computed.component.value"
                        :key="views.state.activeView.value"
                        :value="views.state.activeView.value"
                        class="mt-6"
                    >
                        <component
                            :is="views.computed.component.value"
                            v-bind="{ ...views.computed.props.value }"
                        />
                    </TabsContent>
                </Transition>
            </Tabs>
        </div>

        <div class="my-24" />
    </div>
</template>
