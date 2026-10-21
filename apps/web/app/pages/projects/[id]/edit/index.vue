<script setup lang="ts">
    import { toast } from "vue-sonner";

    definePageMeta({
        title: "projects.edit.title",
        layout: "sidebar",
        middleware: ["sidebase-auth", "project-validation", "internal-callback-url"],
        i18n: {
            paths: {
                en: "/projects/[id]/edit",
                es: "/proyectos/[id]/editar",
            },
        },
        breadcrumb: {
            options: {
                parent: {
                    kind: "link",
                    overrides: {
                        label: {
                            keypath: "PROJECT_TITLE",
                        },
                    },
                },
            },
        },
    });

    const { $localeRoute } = useNuxtApp();
    const runtimeConfig = useRuntimeConfig();
    const { locale } = useI18n();
    const { BREADCRUMB_OVERRIDES } = useGlobalState();
    const projectId = useRouteParams("id");
    const setI18nParams = useSetI18nParams();
    setI18nParams({ en: { id: projectId.value } });
    const { project } = useProvideProjectState(projectId.value?.toString());
    useSeoMeta({
        description: () => $t("projects.edit.header.description"),

        ogImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,
        twitterImage: () => `${runtimeConfig.public.i18n.baseUrl}/icon.jpeg`,

        ogType: "website",
        ogTitle: () => $t("projects.edit.title"),
        ogDescription: () => $t("projects.edit.header.description"),
        ogLocale: () => locale.value.replace("-", "_"),
        ogSiteName: () => $t("layouts.title"),

        twitterCard: "summary_large_image",
        twitterTitle: () => $t("projects.edit.title"),
        twitterDescription: () => $t("projects.edit.header.description"),

        robots: "noindex, nofollow",
    });
    watchEffect(() => {
        BREADCRUMB_OVERRIDES.value.PROJECT_TITLE = project.value.name;
    });

    const errorToast = useErrorToast();
    const { navigate } = useCallbackUrl(
        $localeRoute({ name: "projects-id", params: { id: projectId.value?.toString() } }),
    );

    async function handleSuccess() {
        toast.success($t("projects.edit.events.project_updated.title"));

        await refreshNuxtData(NuxtKeys.Projects.Id);

        navigate();
    }
</script>

<template>
    <div>
        <ProjectUpdateForm
            :project="project"
            class="mx-auto w-full max-w-5xl"
            @sucess="handleSuccess"
            @error="(error) => errorToast.handleServer(error)"
            @cancel="() => navigate()"
        />
        <div class="my-6" />
    </div>
</template>
