<script setup lang="ts">
    import { ChevronsRight, Clock } from "lucide-vue-next";
    import { cn } from "~/lib/utils";

    const { tables } = useProject();

    const tableName = computed(() => {
        if (!tables.state.value.selectedSchema) {
            return;
        }

        return TableUtils.getTableName(tables.state.value.selectedSchema.import_name);
    });

    const properties = computed(() => {
        const schema = tables.state.value.selectedSchema?.active_schema;
        if (!schema) {
            return;
        }

        return Object.entries(schema.properties).map(([column, config]): [string, typeof config] => [
            column,
            {
                ...config,
                optional: config.optional ?? !schema.required.includes(column),
            },
        ]);
    });

    const animations = useCollapsibleAnimations();
</script>

<template>
    <Card v-if="tables.state.value.selectedSchema" class="overflow-hidden">
        <CardHeader>
            <CardTitle class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <Badge variant="default">
                        {{ $t("projects.id.sections.tables.details.overview.active") }}
                    </Badge>
                    <span>
                        {{
                            $t("projects.id.sections.tables.details.overview.columns", {
                                count: properties?.length || 0,
                            })
                        }}
                    </span>
                </div>
                <div class="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock class="size-3.5" />
                    {{
                        new Date(tables.state.value.selectedSchema.created_at).toLocaleDateString(
                            $i18n.locale,
                            {
                                month: "short",
                                day: "numeric",
                                year: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                                timeZone: "UTC",
                            },
                        )
                    }}
                </div>
            </CardTitle>
        </CardHeader>

        <Separator />

        <CardContent class="space-y-4">
            <div class="flex items-center space-x-2 text-xs text-muted-foreground">
                <span class="font-medium">
                    {{ $t("projects.id.sections.tables.details.overview.schema") }}
                </span>
                <code class="rounded bg-muted px-1.5 py-0.5">
                    {{ tables.state.value.selectedSchema.active_schema.$schema }}
                </code>
            </div>

            <ProjectTablesDetailsPropertiesTable v-if="properties" :properties="properties" />

            <Collapsible v-slot="{ open }">
                <CollapsibleTrigger as-child>
                    <Item class="bg-muted/30 h-12 py-1.5 cursor-pointer">
                        <ItemContent>
                            <ItemTitle>
                                {{ $t("projects.id.sections.tables.details.overview.raw_json") }}
                            </ItemTitle>
                        </ItemContent>
                        <ItemActions>
                            <ChevronsRight :class="cn('size-5 transition-transform', open && 'rotate-90')" />
                        </ItemActions>
                    </Item>
                </CollapsibleTrigger>
                <Transition :css="false" @enter="animations.onEnter" @leave="animations.onLeave">
                    <CollapsibleContent v-if="open" force-mount class="mt-4">
                        <CodeBlock :file="tableName" :content="tables.state.value.selectedSchema.active_schema" />
                    </CollapsibleContent>
                </Transition>
            </Collapsible>
        </CardContent>
    </Card>
</template>
