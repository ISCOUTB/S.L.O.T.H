import type { MongoRaw, ResponseProject } from "#shared/utils/schemas/types";
import { v7 } from "uuid";

function $<T>(context: T | undefined, defaultValue: string, value: (value: T) => string) {
    if (!context) {
        return defaultValue;
    }

    return value(context);
}

function $$<A, B>(
    a: A | undefined,
    b: B | undefined,
    defaults: {
        none: string;
        onlyA: (a: A) => string;
        both: (a: A, b: B) => string;
    },
) {
    if (!a) {
        return defaults.none;
    }

    if (!b) {
        return defaults.onlyA(a);
    }

    return defaults.both(a, b);
}

export const NuxtKeys = {
    Projects: {
        Id: "projects:id",
        Search: "projects:search",
        SharedState: (candidateId: ResponseProject["id"] | undefined) =>
            $(candidateId, "project:state", (value) => `project:${value}:state`),
        Schemas: {
            SchemaState: (projectId: ResponseProject["id"] | undefined) =>
                $(projectId, "project:shared-state", (value) => `project:${value}:shared-state`),
            Errors: (projectId: ResponseProject["id"] | undefined) =>
                $(
                    projectId,
                    "project:schemas-errors",
                    (value) => `project:${value}:schemas-errors`,
                ),
            ExampleFormat: "project:schema:example-format",
            RowId: "__rowId",
        },
        Tables: {
            TableState: (projectId: ResponseProject["id"] | undefined) =>
                $(projectId, "project:tables", (value) => `project:${value}:tables`),
            CollapsibleState: (table: MongoRaw) => `project:table:${table.id}:collapsible:open`,
            RawSchemas: (projectId: ResponseProject["id"] | undefined) =>
                $(projectId, "project:raw-schemas", (value) => `project:${value}:raw-schemas`),
            View: (projectId: ResponseProject["id"] | undefined) =>
                $(projectId, "project:tables:view", (value) => `project:${value}:tables:view`),
            TabsManager: (route: string) => `project:tables:${route}:tabs-manager`,
            SharedState: (
                projectId: ResponseProject["id"] | undefined,
                tableName: MongoRaw["import_name"] | undefined,
            ) =>
                $$(projectId, tableName, {
                    none: "project:tables:shared-state",
                    onlyA: (id) => `project:${id}:tables:shared-state`,
                    both: (id, name) => `project:${id}:tables:${name}:shared-state`,
                }),
            Tasks: (
                projectId: ResponseProject["id"] | undefined,
                tableName: MongoRaw["import_name"] | undefined,
            ) =>
                $$(projectId, tableName, {
                    none: "project:tables:tasks",
                    onlyA: (id) => `project:${id}:tables:tasks`,
                    both: (id, name) => `project:${id}:tables:${name}:tasks`,
                }),
        },
        Edit: {
            TableName: (
                projectId: ResponseProject["id"] | undefined,
                tableName: MongoRaw["import_name"] | undefined,
            ) =>
                $$(projectId, tableName, {
                    none: "project:tables:edit:table-name",
                    onlyA: (id) => `project:${id}:tables:edit:table-name`,
                    both: (id, name) => `project:${id}:tables:${name}:edit:table-name`,
                }),
            ColumnState: (
                projectId: ResponseProject["id"] | undefined,
                tableName: MongoRaw["import_name"] | undefined,
            ) =>
                $$(projectId, tableName, {
                    none: "project:tables:edit:columns",
                    onlyA: (id) => `project:${id}:tables:edit:columns`,
                    both: (id, name) => `project:${id}:tables:${name}:edit:columns`,
                }),
        },
        QueryBuilder: {
            SelectedSchema: (projectId: ResponseProject["id"]) =>
                $(
                    projectId,
                    "project:query-builder:selected-schema",
                    (value) => `project:${value}:selected-schema`,
                ),
            SelectedOutput: (
                projectId: ResponseProject["id"] | undefined,
                tableName: MongoRaw["import_name"] | undefined,
            ) =>
                $$(projectId, tableName, {
                    none: "project:query-builder:selected-output",
                    onlyA: (id) => `project:${id}:query-builder:selected-output`,
                    both: (id, name) => `project:${id}:query-builder:${name}:selected-output`,
                }),
            Rows: (projectId: ResponseProject["id"] | undefined) =>
                $(
                    projectId,
                    "project:query-builder:rows",
                    (id) => `project:${id}:query-builder:rows`,
                ),
        },
        CookieTab: (projectId: ResponseProject["id"] | undefined) =>
            $(projectId, "sloth:project:tab", (id) => `sloth:project:${id}:tab`),
    },
    Components: {
        DataTable: {
            Sorting: (route: string) => `data-table:sorting-state:${route}`,
        },
        QueryBuilder: {
            SelectedColumns: (schema: MongoRaw | undefined) =>
                $(
                    schema,
                    "query-builder:selected-columns",
                    (value) => `query-builder:${value.id}:selected-columns`,
                ),
            WhereTree: (schema: MongoRaw | undefined) =>
                $(
                    schema,
                    "query-builder:where-tree",
                    (value) => `query-builder:${value.id}:where-tree`,
                ),
            OrderBy: (schema: MongoRaw | undefined) =>
                $(
                    schema,
                    "query-builder:order-by",
                    (value) => `query-builder:${value.id}:order-by`,
                ),
            Limit: (schema: MongoRaw | undefined) =>
                $(schema, "query-builder:limit", (value) => `query-builder:${value.id}:limit`),
            Rows: (route: string) => `query-builder:${route}:rows`,
        },
        InputPassword: () => `input:${v7()}`,
    },
    Composables: {
        ViewManager: {
            StateKey: (route: string) => `view-manager:${route}:state-key`,
            ActiveView: (stateKey: string) => `${stateKey}:active-view`,
        },
    },
    Sidebar: {
        OpenCollapsible: (group: Components.Sidebar.GroupCollapsibleKind) =>
            `sidebar:${group.kind}:${group.label}`,
        CookieOpen: "sloth:sidebar_state",
    },
    Params: {
        NoDefaultValue: "keys:params:default-value",
        PreviousRoute: "keys:params:previous-route",
    },
    GlobalState: "state:global",
} as const;

export const ModalKeys = {
    Projects: {
        Delete: {
            ConfirmationModal: "projects:delete:confirmation-modal",
        },
        Schema: {
            UploadSchema: "projects:schema:upload-schema",
        },
        Tables: {
            Delete: "projects:tables:delete-schema",
        },
        QueryBuilder: {
            Generate: "project:query-builder:generate",
        },
    },
} as const;

export const WebSocketKeys = {
    User: {
        Connected: (id: string) => `user:connected:${id}`,
    },
};
