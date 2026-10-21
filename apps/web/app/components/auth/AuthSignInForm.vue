<script setup lang="ts">
    interface Emits {
        success: [email: string];
        error: [error: string];
    }

    const emit = defineEmits<Emits>();

    const email = useRouteQuery<string>("email", "");
    const { SignInSchema } = useSignInSchema();
    const { handleSubmit } = useForm({
        validationSchema: toTypedSchema(SignInSchema.value),
        initialValues: {
            email: email.value,
            password: "",
        },
    });

    const auth = useAuth();

    const [loading] = useToggle(false);
    const onSubmit = handleSubmit((values) => {
        loading.value = true;

        auth.signIn("credentials", {
            email: values.email,
            password: values.password,
            redirect: false,
        })
            .then((response) => {
                if (response.error) {
                    emit("error", response.error);
                    return;
                }

                if (response.ok) {
                    emit("success", values.email);
                }
            })
            .finally(() => (loading.value = false));
    });

    const { service } = useAppServices();
</script>

<template>
    <form @submit="onSubmit">
        <FieldGroup>
            <VeeField v-slot="{ field, errors }" name="email">
                <Field :data-invalid="!!errors.length">
                    <FieldLabel for="email">
                        {{ $t("auth.fields.email.label") }}
                    </FieldLabel>
                    <Input
                        id="email"
                        v-bind="field"
                        v-model="email"
                        type="email"
                        :placeholder="$t('auth.fields.email.placeholder')"
                        autocomplete="email"
                        :aria-invalid="!!errors.length"
                    />
                    <FieldError v-if="errors.length" :errors="errors" />
                </Field>
            </VeeField>

            <VeeField v-slot="{ field, errors }" name="password">
                <Field :data-invalid="!!errors.length">
                    <FieldLabel for="password">
                        {{ $t("auth.fields.password.label") }}
                    </FieldLabel>
                    <InputPassword
                        id="password"
                        v-bind="field"
                        :placeholder="$t('auth.fields.password.placeholder')"
                        autocomplete="current-password"
                        :aria-invalid="!!errors.length"
                    />
                    <FieldError v-if="errors.length" :errors="errors" />
                </Field>
            </VeeField>

            <Field>
                <Button :disabled="loading || !service('auth.signIn')" type="submit">
                    <UtilsLoading :loading="loading" />
                    {{ $t("auth.sign_in.submit") }}
                </Button>
            </Field>

            <FieldDescription>
                {{ $t("auth.sign_in.create_account") }}
                <NuxtLinkLocale
                    :to="{ name: 'auth-sign-up' }"
                    class="font-medium text-foreground underline underline-offset-4 transition-colors hover:text-foreground/80"
                >
                    {{ $t("auth.sign_in.sign_up_link") }}
                </NuxtLinkLocale>
            </FieldDescription>
        </FieldGroup>
    </form>
</template>
