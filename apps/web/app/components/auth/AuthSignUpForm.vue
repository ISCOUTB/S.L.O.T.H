<script setup lang="ts">
    import { UserResponse } from "#shared/utils/schemas/auth";

    interface Emits {
        success: [email: string];
        error: [error: unknown];
    }

    const emit = defineEmits<Emits>();

    const { SignUpSchema } = useSignUpSchema();
    const { handleSubmit } = useForm({
        validationSchema: toTypedSchema(SignUpSchema.value),
        initialValues: {
            name: "",
            email: "",
            password: "",
            confirm: "",
        },
    });

    const { $api } = useNuxtApp();
    const [loading] = useToggle(false);
    const onSubmit = handleSubmit((values) => {
        const formData = new FormBuilder()
            .append("username", values.name)
            .append("email", values.email)
            .append("password", values.password)
            .build();

        loading.value = true;
        $api("/auth/sign-up", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                const parsedResponse = UserResponse.safeParse(response);

                if (!parsedResponse.success) {
                    throw createError({});
                }

                emit("success", parsedResponse.data.email);
            })
            .catch((error) => emit("error", error))
            .finally(() => (loading.value = false));
    });

    const { service } = useAppServices();
</script>

<template>
    <form @submit="onSubmit">
        <FieldGroup>
            <VeeField v-slot="{ field, errors }" name="name">
                <Field :data-invalid="!!errors.length">
                    <FieldLabel for="name">
                        {{ $t("auth.fields.username.label") }}
                    </FieldLabel>
                    <Input
                        id="name"
                        v-bind="field"
                        :placeholder="$t('auth.fields.username.placeholder')"
                        autocomplete="name"
                        :aria-invalid="!!errors.length"
                    />
                    <FieldError v-if="errors.length" :errors="errors" />
                </Field>
            </VeeField>

            <VeeField v-slot="{ field, errors }" name="email">
                <Field :data-invalid="!!errors.length">
                    <FieldLabel for="email">
                        {{ $t("auth.fields.email.label") }}
                    </FieldLabel>
                    <Input
                        id="email"
                        type="email"
                        v-bind="field"
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

            <VeeField v-slot="{ field, errors }" name="confirm">
                <Field :data-invalid="!!errors.length">
                    <FieldLabel for="confirm">
                        {{ $t("auth.fields.confirm_password.label") }}
                    </FieldLabel>
                    <InputPassword
                        id="confirm"
                        v-bind="field"
                        :placeholder="$t('auth.fields.confirm_password.placeholder')"
                        autocomplete="current-password"
                        :aria-invalid="!!errors.length"
                    />
                    <FieldError v-if="errors.length" :errors="errors" />
                </Field>
            </VeeField>

            <Field>
                <Button :disabled="loading || !service('auth.signUp')" type="submit">
                    <UtilsLoading :loading="loading" />
                    {{ $t("auth.sign_up.submit") }}
                </Button>
            </Field>

            <FieldDescription>
                {{ $t("auth.sign_up.has_account") }}
                <NuxtLinkLocale
                    :to="{ name: 'auth-sign-in' }"
                    class="font-medium text-foreground underline underline-offset-4 transition-colors hover:text-foreground/80"
                >
                    {{ $t("auth.sign_up.sign_in_link") }}
                </NuxtLinkLocale>
            </FieldDescription>
        </FieldGroup>
    </form>
</template>
