declare global {
    type Prettify<T> = {
        [K in keyof T]: T[K];
    } & {};

    type MergeTypes<TypesArray extends unknown[], Res = object> = TypesArray extends [
        infer Head,
        ...infer Rem,
    ]
        ? MergeTypes<Rem, Res & Head>
        : Res;

    type OneOf<
        TypesArray extends unknown[],
        Res = never,
        AllProperties = MergeTypes<TypesArray>,
    > = TypesArray extends [infer Head, ...infer Rem]
        ? OneOf<Rem, Res | OnlyFirst<Head, AllProperties>, AllProperties>
        : Res;

    type OnlyFirst<F, S> = F & { [Key in keyof Omit<S, keyof F>]?: never };

    type ArrayType<T> = T extends (infer U)[] ? U : never;

    type ChangePropertyType<T extends object, K extends keyof T, NewType> = {
        [P in keyof T]: P extends K ? NewType : T[P];
    };

    type ChangeProperties<T extends object, PropTypeMap extends { [K in keyof T]?: unknown }> = {
        [P in keyof T]: P extends keyof PropTypeMap ? PropTypeMap[P] : T[P];
    };

    type MakeRefs<T extends object> = {
        [P in keyof T]: Ref<T[P]>;
    };

    type Branded<T, Brand> = T & { __brand: Brand };

    type DotNotation<T, Prefix extends string = ""> = {
        [K in keyof T]: T[K] extends Record<string, unknown>
            ? DotNotation<T[K], `${Prefix}${K & string}.`>
            : `${Prefix}${K & string}`
    }[keyof T];
}

export { };
