<script setup lang="ts">
    import { ArrowLeft, Pencil, Pickaxe, Table2, Trash2 } from "lucide-vue-next";

    const { project, tables, queryBuilder, VIEWS } = useProject();

    const tableName = computed(() => {
        if (!tables.state.value.selectedSchema) {
            return;
        }

        return TableUtils.getTableName(tables.state.value.selectedSchema.import_name);
    });

    const events = useAppEvents();
    function handleBack(_event: Event) {
        events.emit("event:projects:table:change-view", { value: "list" });
    }

    const modal = useModal();
    function handleDelete(_event: Event) {
        if (!project.value) {
            return;
        }

        modal.dispatch.loadComponent({
            loader: () => import("~/components/project/tables/ProjectTablesDeleteModal.vue"),
            key: ModalKeys.Projects.Tables.Delete,
            props: {
                table: tables.state.value.selectedSchema,
                projectId: project.value.id,
                kind: "delete",
                onSuccess: () => {
                    events.emit("event:projects:table:change-view", { value: "list" });
                    tables.dispatch.setSelectedSchema(undefined);
                },
            },
        });
    }

    function handleQuery(_event: Event) {
        queryBuilder.state.schema.value = tables.state.value.selectedSchema;
        events.emit("event:projects:change-tab", { value: VIEWS.value.QueryBuilder.value });
    }
</script>

<template>
    <div>
        <div class="flex flex-col space-y-6">
            <div class="flex items-center gap-4">
                <Button variant="ghost" size="icon" class="shrink-0" @click="handleBack">
                    <ArrowLeft class="size-4" />
                    <span class="sr-only">
                        {{ $t("projects.id.sections.tables.details.back") }}
                    </span>
                </Button>
                <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-3">
                        <div class="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                            <Table2 class="size-5 text-primary" />
                        </div>
                        <div>
                            <h2 class="text-lg font-medium text-foreground">
                                {{ tableName }}
                            </h2>
                            <p class="text-xs text-muted-foreground font-mono">
                                {{ tables.state.value.selectedSchema?.id }}
                            </p>
                        </div>
                    </div>
                </div>

                <div class="space-x-2">
                    <Button variant="outline" @click="handleQuery">
                        <Pickaxe />
                        {{ $t('projects.id.sections.tables.details.query_table') }}
                    </Button>
                    <Button v-if="project" variant="outline" as-child>
                        <NuxtLink
                            :to="$localePath({
                                name: 'projects-id-tables-tableName-edit',
                                params: { id: project.id, tableName },
                                query: {
                                    callbackUrl: $route.fullPath,
                                },
                            })
                            "
                        >
                            <Pencil class="size-4" />
                            {{ $t("projects.id.sections.tables.details.edit") }}
                        </NuxtLink>
                    </Button>
                    <Button
                        v-if="tables.state.value.selectedSchema" variant="destructive"
                        :disabled="tables.state.value.selectedSchema.schemas_releases.length > 0" class="cursor-pointer"
                        @click="handleDelete"
                    >
                        <Trash2 class="size-4" />
                        {{ $t("projects.id.sections.tables.details.delete") }}
                    </Button>
                </div>
            </div>

            <ProjectTablesDetailsOverview />
            <ProjectTablesDetailsUploadFile />
            <ProjectTablesDetailsTasks />
            <ProjectTablesDetailsVersionHistory />
        </div>
    </div>
</template>
