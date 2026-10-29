<script setup lang="ts">
    import { PaginatedResponse, ResponseProjectSchema } from "#shared/utils/schemas/api";
    import {
        AlignLeft,
        ChevronsLeft,
        ChevronsRight,
        Plug,
        Plus,
        Search,
        Server,
        UserSearch,
    } from "lucide-vue-next";

    definePageMeta({
        title: "projects.view.title",
        layout: "sidebar",
        middleware: ["sidebase-auth"],
        i18n: {
            paths: {
                en: "/projects",
                es: "/proyectos",
            },
        },
        breadcrumb: {
            options: {
                parent: {
                    kind: "link",
                },
            },
        },
    });

    const { locale } = useI18n();
    const runtimeConfig = useRuntimeConfig();

    useSeoMeta({
        description: () => $t("projects.view.header.description"),

        ogImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,
        twitterImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,

        ogType: "website",
        ogTitle: () => $t("projects.view.title"),
        ogDescription: () => $t("projects.view.header.description"),
        ogLocale: () => locale.value.replace("-", "_"),
        ogSiteName: () => $t("layouts.title"),

        twitterCard: "summary_large_image",
        twitterTitle: () => $t("projects.view.title"),
        twitterDescription: () => $t("projects.view.header.description"),

        robots: "index, follow",
    });

    const { $localeRoute } = useNuxtApp();
    const errorToast = useErrorToast();
    const config = useAppConfig();
    const Response = PaginatedResponse(ResponseProjectSchema);

    const currentPage = useRouteQuery("page", 1, {
        transform: Number,
        mode: "replace",
    });
    const searchContent = useState("search-content", () => "");
    const debouncedSearchContent = useDebounce(searchContent, 1000);
    const calculatedSkip = computed(
        () => (currentPage.value - 1) * config.pagination.defaultPageSize,
    );

    const ownerId = useRouteQuery<string | null>(config.constants.OWNER_ID_KEY, null);

    const { data: _data, status } = useApiFetch("/projects/search", {
        query: {
            name: debouncedSearchContent,
            owner_id: ownerId,
            skip: calculatedSkip,
            limit: config.pagination.defaultPageSize,
        },
        key: NuxtKeys.Projects.Search,
    });
    const data = computed(() => {
        if (!_data.value) {
            return;
        }

        const parsed = Response.safeParse(_data.value);
        if (!parsed.success) {
            errorToast.handle(ResponseCodesRecord.Server.BadPayload);
            return;
        }

        return parsed.data;
    });

    function makeInfo(project: ResponseProject): Schemas.Project.ProjectInformation[] {
        return [
            {
                label: $t("projects.create.fields.db_host.label"),
                value: project.db_host,
                fallbackValue: $t("projects.create.fields.db_host.label"),
                icon: Server,
                warning: !project.db_host,
                tooltip: $t("projects.view.content.no_field", {
                    field: $t("projects.create.fields.db_host.label"),
                }),
            },
            {
                label: $t("projects.create.fields.db_port.label"),
                value: project.db_port?.toString(),
                fallbackValue: $t("projects.create.fields.db_port.label"),
                icon: Plug,
                warning: !project.db_port,
                tooltip: $t("projects.view.content.no_field", {
                    field: $t("projects.create.fields.db_port.label"),
                }),
            },
            {
                label: $t("projects.create.fields.db_name.label"),
                value: project.db_name,
                fallbackValue: $t("projects.create.fields.db_name.label"),
                icon: AlignLeft,
                warning: !project.db_name,
                tooltip: $t("projects.view.content.no_field", {
                    field: $t("projects.create.fields.db_name.label"),
                }),
            },
        ];
    }
</script>

<template>
    <div class="mx-auto w-full max-w-5xl flex flex-col grow">
        <TooltipProvider>
            <div class="space-y-6">
                <div class="space-y-8">
                    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                        <div class="space-y-1.5">
                            <h1
                                class="text-2xl font-semibold tracking-tight text-foreground text-balance"
                            >
                                {{ $t("projects.view.header.title") }}
                            </h1>
                            <p class="text-sm text-muted-foreground">
                                {{ $t("projects.view.header.description") }}
                            </p>
                        </div>

                        <div class="space-x-2 flex items-center flex-wrap">
                            <NuxtLink as-child :to="$localeRoute({ name: 'projects-create' })">
                                <Button>
                                    <Plus class="size-4" />
                                    <span>{{ $t("projects.create.header.title") }}</span>
                                </Button>
                            </NuxtLink>
                            <AuthRole v-if="ownerId">
                                <Button variant="outline" @click="ownerId = null">
                                    <UserSearch />
                                    {{ $t("projects.view.actions.clear_owner_filter") }}
                                </Button>
                            </AuthRole>
                        </div>
                    </div>

                    <div>
                        <InputGroup class="max-w-sm">
                            <InputGroupInput
                                v-model="searchContent"
                                :placeholder="$t('projects.view.search_input.placeholder')"
                            />
                            <InputGroupAddon align="inline-start">
                                <Search />
                            </InputGroupAddon>
                        </InputGroup>
                    </div>
                </div>
                <PaginationRoot
                    :items="data?.items"
                    index="id"
                    :page="currentPage"
                    :loading="status === 'pending'"
                    :page-size="data?.limit ?? config.pagination.defaultPageSize"
                    :total-pages="data?.total_pages ?? 1"
                    class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
                    @change-page="(page) => (currentPage = page)"
                >
                    <template #controls-previous>
                        <ChevronsLeft />
                    </template>
                    <template #controls-next>
                        <ChevronsRight />
                    </template>

                    <template #empty>
                        <LazyProjectEmpty />
                    </template>

                    <template #loading>
                        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                            <template v-for="i in config.pagination.defaultPageSize" :key="i">
                                <Skeleton class="w-full h-82.5" />
                            </template>
                        </div>
                    </template>

                    <template #item="{ $item }">
                        <ProjectCard :project="$item" :make-info="makeInfo" />
                    </template>
                </PaginationRoot>
            </div>
        </TooltipProvider>
    </div>
</template>
