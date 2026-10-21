<script setup lang="ts">
    import type { UserRole } from "#shared/utils/schemas/types";
    import {
        Boxes,
        ChevronsLeft,
        ChevronsRight,
        Search,
        ShieldCheck,
        UserIcon,
    } from "lucide-vue-next";
    import { cn } from "@/lib/utils";

    definePageMeta({
        title: "admin.users.title",
        layout: "sidebar",
        middleware: ["sidebase-auth", "sudo"],
        breadcrumb: {
            label: "admin.users.title",
            options: {
                parent: {
                    options: {
                        parent: {
                            kind: "link",
                        },
                    },
                },
            },
        },
        i18n: {
            paths: {
                en: "/admin/users",
                es: "/administrador/usuarios",
            },
        },
    });

    const { locale } = useI18n();
    const runtimeConfig = useRuntimeConfig();

    useSeoMeta({
        description: () => $t("admin.users.header.description"),

        ogImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,
        twitterImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,

        ogType: "website",
        ogTitle: () => $t("admin.users.title"),
        ogDescription: () => $t("admin.users.header.description"),
        ogLocale: () => locale.value.replace("-", "_"),
        ogSiteName: () => $t("layouts.title"),

        twitterCard: "summary_large_image",
        twitterTitle: () => $t("admin.users.title"),
        twitterDescription: () => $t("admin.users.header.description"),

        robots: "noindex, nofollow",
    });

    const auth = useAuth();

    const config = useAppConfig();
    const currentPage = useRouteQuery("page", 1, {
        transform: Number,
        mode: "replace",
    });
    const searchContent = useState("search-content", () => "");
    const debouncedSearchContent = useDebounce(searchContent, 1000);
    const calculatedSkip = computed(
        () => (currentPage.value - 1) * config.pagination.defaultPageSize,
    );

    const Response = PaginatedResponse(UserResponse);
    const { data: _data, status } = useApiFetch("/users/search", {
        query: {
            email: debouncedSearchContent,
            skip: calculatedSkip,
            limit: config.pagination.defaultPageSize,
        },
        key: "users",
    });

    const { $logger } = useNuxtApp();
    const errorToast = useErrorToast();
    const data = computed(() => {
        $logger.info("parsing data");
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

    function resolveRoleIcon(role: UserRole): Components.LucideIconComponent {
        if (role === "sudo") {
            return ShieldCheck;
        }

        return UserIcon;
    }
</script>

<template>
    <div class="mx-auto w-full max-w-5xl">
        <div class="space-y-4">
            <div class="space-y-1.5">
                <h1 class="text-2xl font-semibold tracking-tight text-foreground text-balance">
                    {{ $t("admin.users.title") }}
                </h1>
                <p class="text-sm text-muted-foreground">
                    {{ $t("admin.users.header.description") }}
                </p>
            </div>

            <div>
                <InputGroup class="max-w-sm">
                    <InputGroupInput
                        v-model="searchContent"
                        :placeholder="$t('admin.users.search_input.placeholder')"
                    />
                    <InputGroupAddon align="inline-start">
                        <Search />
                    </InputGroupAddon>
                </InputGroup>
            </div>

            <PaginationRoot
                :items="data?.items"
                index="id"
                :page="currentPage"
                :loading="status === 'pending'"
                :page-size="data?.limit ?? config.pagination.defaultPageSize"
                :total-pages="data?.total_pages ?? 1"
                class="space-y-4"
                @change-page="(page) => (currentPage = page)"
            >
                <template #controls-previous>
                    <ChevronsLeft />
                </template>
                <template #controls-next>
                    <ChevronsRight />
                </template>

                <template #item="{ $item }">
                    <Item variant="outline">
                        <ItemMedia>
                            <Avatar>
                                <AvatarFallback class="text-sm font-medium">
                                    {{ extractAvatarFallback($item.name) }}
                                </AvatarFallback>
                            </Avatar>
                        </ItemMedia>
                        <ItemContent>
                            <ItemTitle>
                                <span class="text-sm font-medium text-foreground truncate">
                                    {{ $item.name }}
                                </span>
                                <Badge
                                    v-if="$item.email === auth.data.value?.user.email"
                                    variant="outline"
                                    class="text-xs border-emerald-500 text-emerald-500"
                                >
                                    {{ $t("admin.users.badges.you") }}
                                </Badge>
                            </ItemTitle>
                            <ItemDescription class="text-xs text-muted-foreground truncate">
                                {{ $item.email }}
                            </ItemDescription>
                        </ItemContent>
                        <ItemActions>
                            <div class="space-x-4 flex items-center">
                                <TooltipProvider>
                                    <Tooltip>
                                        <TooltipTrigger as-child>
                                            <div
                                                class="size-2 rounded-full shrink-0"
                                                :class="
                                                    cn(
                                                        $item.status === 'active'
                                                            ? 'bg-emerald-500'
                                                            : 'bg-muted-foreground/40',
                                                    )
                                                "
                                            />
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p class="text-xs capitalize">
                                                {{
                                                    $te(`admin.users.status.${$item.status}`)
                                                        ? $t(`admin.users.status.${$item.status}`)
                                                        : $item.status
                                                }}
                                            </p>
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                                <TooltipProvider>
                                    <Tooltip>
                                        <TooltipTrigger as-child>
                                            <div class="shrink-0 text-muted-foreground">
                                                <component
                                                    :is="resolveRoleIcon($item.role)"
                                                    :class="
                                                        cn(
                                                            'size-5',
                                                            $item.role === 'sudo' &&
                                                                'text-amber-500',
                                                        )
                                                    "
                                                />
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p class="text-xs capitalize">{{ $item.role }}</p>
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>

                                <Button variant="outline" as-child>
                                    <NuxtLink
                                        :to="
                                            $localeRoute({
                                                name: 'projects',
                                                query: {
                                                    [config.constants.OWNER_ID_KEY]: $item.id,
                                                },
                                            })
                                        "
                                    >
                                        <Boxes />
                                        {{ $t("projects.title") }}
                                    </NuxtLink>
                                </Button>
                            </div>
                        </ItemActions>
                    </Item>
                </template>
            </PaginationRoot>
        </div>
    </div>
</template>
