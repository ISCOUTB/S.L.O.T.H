export default function () {
    const { public: { services } } = useRuntimeConfig();

    function service(key: DotNotation<typeof services>): boolean {
        return key.split(".").reduce((obj: any, k) => obj?.[k], services) ?? false;
    }

    return { service };
}
